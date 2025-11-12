"""FastAPI web service for batch2md."""

import asyncio
import uuid
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tempfile

from .models import (
    ConversionConfig,
    ConversionJob,
    ConversionStatus,
    ConversionSummary,
    SupportedFormat
)
from .scanner import scan_documents
from .converters import convert_to_pdf, convert_to_markdown, extract_images
from .output_manager import (
    resolve_output_path,
    create_output_directories,
    get_images_dir
)


# Request/Response Models
class ConversionRequest(BaseModel):
    """Request to start a conversion job."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    recursive: bool = True
    overwrite: bool = False
    backend: str = "pipeline"
    timeout: int = 300


class ConversionJobResponse(BaseModel):
    """Response for a conversion job."""
    job_id: str
    status: str
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    error: Optional[str] = None
    progress: int = 0
    total_files: int = 0
    completed_files: int = 0
    failed_files: int = 0
    current_file: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class UploadResponse(BaseModel):
    """Response for file upload."""
    upload_id: str
    files: List[str]
    message: str


# Global job storage (in production, use Redis or database)
jobs: Dict[str, Dict] = {}
upload_storage: Dict[str, Path] = {}

# Create FastAPI app
app = FastAPI(
    title="Batch2MD API",
    description="Batch convert documents to Markdown via PDF using MinerU",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Batch2MD API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.post("/api/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload files for conversion.

    Args:
        files: List of files to upload

    Returns:
        UploadResponse with upload_id and file list
    """
    upload_id = str(uuid.uuid4())
    upload_dir = Path(tempfile.mkdtemp(prefix=f"batch2md_upload_{upload_id}_"))
    print(f"[Upload] Created upload directory: {upload_dir}")

    uploaded_files = []
    for file in files:
        # Save uploaded file
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        uploaded_files.append(file.filename)
        print(f"[Upload] Saved file: {file.filename} ({len(content)} bytes)")

    # Store upload directory
    upload_storage[upload_id] = upload_dir
    print(f"[Upload] Stored upload_id {upload_id} with {len(uploaded_files)} files")

    return UploadResponse(
        upload_id=upload_id,
        files=uploaded_files,
        message=f"Uploaded {len(uploaded_files)} file(s)"
    )


@app.post("/api/convert", response_model=ConversionJobResponse)
async def create_conversion_job(request: ConversionRequest):
    """
    Create a new conversion job.

    Args:
        request: ConversionRequest with job parameters

    Returns:
        ConversionJobResponse with job_id
    """
    job_id = str(uuid.uuid4())

    # Determine input path
    if request.input_path:
        # Check if this is an upload_id (format: upload://uuid)
        if request.input_path.startswith("upload://"):
            upload_id = request.input_path.replace("upload://", "")
            if upload_id not in upload_storage:
                raise HTTPException(status_code=400, detail=f"Upload ID not found: {upload_id}")
            input_path = upload_storage[upload_id]
        else:
            input_path = Path(request.input_path)
            if not input_path.exists():
                raise HTTPException(status_code=400, detail=f"Input path not found: {request.input_path}")
    else:
        raise HTTPException(status_code=400, detail="input_path is required")

    # Determine output path
    if request.output_path:
        output_path = Path(request.output_path)
    else:
        # For uploaded files, create output in temp directory
        if request.input_path.startswith("upload://"):
            output_path = Path(tempfile.mkdtemp(prefix=f"batch2md_output_{job_id}_"))
        else:
            output_path = input_path / "markdown"

    # Create job record
    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "input_path": str(input_path),
        "output_path": str(output_path),
        "config": request,
        "progress": 0,
        "total_files": 0,
        "completed_files": 0,
        "failed_files": 0,
        "current_file": None,
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "error": None,
        "results": []
    }

    print(f"[API] Created job {job_id} with input_path={input_path}, output_path={output_path}")

    # Start conversion in background
    asyncio.create_task(run_conversion_job(job_id))
    print(f"[API] Started background task for job {job_id}")

    return ConversionJobResponse(
        job_id=job_id,
        status="pending",
        input_path=str(input_path),
        output_path=str(output_path)
    )


@app.get("/api/jobs/{job_id}", response_model=ConversionJobResponse)
async def get_job_status(job_id: str):
    """
    Get status of a conversion job.

    Args:
        job_id: Job ID

    Returns:
        ConversionJobResponse with job status
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return ConversionJobResponse(
        job_id=job["job_id"],
        status=job["status"],
        input_path=job["input_path"],
        output_path=job["output_path"],
        error=job.get("error"),
        progress=job["progress"],
        total_files=job["total_files"],
        completed_files=job["completed_files"],
        failed_files=job["failed_files"],
        current_file=job.get("current_file"),
        start_time=job["start_time"],
        end_time=job.get("end_time")
    )


@app.get("/api/jobs/{job_id}/download")
async def download_results(job_id: str):
    """
    Download conversion results as a zip file.

    Args:
        job_id: Job ID

    Returns:
        Zip file with converted markdown files
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")

    output_path = Path(job["output_path"])
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output directory not found")

    # Create zip file
    zip_path = Path(tempfile.mktemp(suffix=".zip"))
    shutil.make_archive(str(zip_path.with_suffix("")), "zip", output_path)

    return FileResponse(
        path=str(zip_path.with_suffix(".zip")),
        media_type="application/zip",
        filename=f"batch2md_results_{job_id}.zip"
    )


@app.websocket("/api/ws/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time progress updates.

    Args:
        websocket: WebSocket connection
        job_id: Job ID
    """
    await websocket.accept()

    try:
        # Send initial status
        if job_id in jobs:
            await websocket.send_json(jobs[job_id])
        else:
            await websocket.send_json({"error": "Job not found"})
            await websocket.close()
            return

        # Keep sending updates
        while True:
            if job_id in jobs:
                job = jobs[job_id]
                await websocket.send_json({
                    "job_id": job["job_id"],
                    "status": job["status"],
                    "progress": job["progress"],
                    "total_files": job["total_files"],
                    "completed_files": job["completed_files"],
                    "failed_files": job["failed_files"],
                    "current_file": job.get("current_file"),
                })

                # Close connection if job is done
                if job["status"] in ["completed", "failed"]:
                    break

            await asyncio.sleep(1)  # Update every second

    except WebSocketDisconnect:
        pass


async def run_conversion_job(job_id: str):
    """
    Run a conversion job in the background.

    Args:
        job_id: Job ID
    """
    job = jobs[job_id]

    try:
        print(f"[Job {job_id}] Starting conversion job...")
        job["status"] = "running"

        # Get configuration
        config_req = job["config"]
        input_path = Path(job["input_path"])
        output_path = Path(job["output_path"])

        print(f"[Job {job_id}] Input path: {input_path}")
        print(f"[Job {job_id}] Output path: {output_path}")
        print(f"[Job {job_id}] Input path exists: {input_path.exists()}")
        print(f"[Job {job_id}] Input path is dir: {input_path.is_dir()}")

        # Create config
        config = ConversionConfig(
            input_dir=input_path,
            output_dir=output_path,
            recursive=config_req.recursive,
            overwrite=config_req.overwrite,
            mineru_backend=config_req.backend,
            mineru_timeout=config_req.timeout,
            verbose=False
        )

        # Scan for documents
        exclude_dirs = [output_path]
        print(f"[Job {job_id}] Scanning for documents...")
        documents = scan_documents(input_path, config.recursive, exclude_dirs)

        job["total_files"] = len(documents)
        print(f"[Job {job_id}] Found {len(documents)} documents")

        if len(documents) == 0:
            print(f"[Job {job_id}] No documents found, marking as completed")
            job["status"] = "completed"
            job["end_time"] = datetime.now().isoformat()
            return

        # Process each document
        completed_count = 0
        failed_count = 0

        for i, doc_path in enumerate(documents, 1):
            job["current_file"] = doc_path.name
            job["progress"] = int((i / len(documents)) * 100)
            print(f"[Job {job_id}] Processing file {i}/{len(documents)}: {doc_path.name}")

            try:
                # Resolve output path
                md_output_path = resolve_output_path(
                    doc_path,
                    output_path,
                    input_path,
                    config.overwrite
                )
                images_dir = get_images_dir(md_output_path)

                # Create directories
                create_output_directories(md_output_path, images_dir)

                # Convert to PDF if needed
                if SupportedFormat.requires_pdf_conversion(doc_path):
                    pdf_path = convert_to_pdf(doc_path, output_path / "temp_pdfs")
                else:
                    pdf_path = doc_path

                # Convert to Markdown
                md_path, mineru_temp_dir = convert_to_markdown(
                    pdf_path,
                    md_output_path,
                    config.mineru_backend,
                    config.mineru_timeout
                )

                # Extract images
                images = extract_images(
                    md_path,
                    mineru_temp_dir,
                    images_dir,
                    pdf_path.stem
                )

                # Cleanup
                try:
                    shutil.rmtree(mineru_temp_dir)
                except Exception:
                    pass

                if SupportedFormat.requires_pdf_conversion(doc_path) and pdf_path.exists():
                    try:
                        pdf_path.unlink()
                    except Exception:
                        pass

                completed_count += 1
                job["completed_files"] = completed_count

                # Store result
                job["results"].append({
                    "input": str(doc_path),
                    "output": str(md_path),
                    "status": "completed",
                    "images": len(images)
                })

            except Exception as e:
                failed_count += 1
                job["failed_files"] = failed_count

                job["results"].append({
                    "input": str(doc_path),
                    "status": "failed",
                    "error": str(e)
                })

        # Job completed
        print(f"[Job {job_id}] Conversion completed. Success: {completed_count}, Failed: {failed_count}")
        job["status"] = "completed"
        job["end_time"] = datetime.now().isoformat()
        job["progress"] = 100

    except Exception as e:
        print(f"[Job {job_id}] ERROR: Job failed with exception: {e}")
        import traceback
        traceback.print_exc()
        job["status"] = "failed"
        job["error"] = str(e)
        job["end_time"] = datetime.now().isoformat()


def main():
    """Entry point for web server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
