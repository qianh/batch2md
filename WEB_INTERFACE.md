# Batch2MD Web Interface

A modern, user-friendly web interface for batch document to Markdown conversion.

## Overview

The Batch2MD web interface provides an intuitive graphical interface for converting documents to Markdown format. Built with React and FastAPI, it offers real-time progress tracking, drag-and-drop file upload, and one-click result downloads.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  React Frontend │ ◄─────► │  FastAPI Backend │
│  (Port 5173)    │   HTTP  │   (Port 8000)    │
│                 │   WS    │                  │
└─────────────────┘         └──────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  batch2md Core   │
                            │  (CLI Logic)     │
                            └──────────────────┘
```

**Frontend (React + TypeScript + Vite)**
- Modern UI with Tailwind CSS styling
- Real-time progress updates via WebSocket
- File upload with drag-and-drop support
- Path-based processing for local directories

**Backend (FastAPI + Python)**
- REST API for job management
- WebSocket for live progress streaming
- Reuses existing batch2md conversion logic
- Handles file uploads and result packaging

## Quick Start

### One-Command Launch

```bash
# Linux/macOS
./scripts/start-web.sh

# Windows
scripts\start-web.bat
```

This will:
1. Install Python web dependencies (`fastapi`, `uvicorn`, `websockets`)
2. Install Node.js frontend dependencies
3. Start backend API on http://localhost:8000
4. Start frontend dev server on http://localhost:5173
5. Open your browser to the web interface

### Manual Launch

**Backend:**
```bash
# Install web dependencies
uv sync --extra web
# or
pip install ".[web]"

# Start API server
uv run batch2md-web
# or
python -m uvicorn batch2md.web_api:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend

# Install dependencies (first time only)
npm install
# or
bun install

# Start dev server
npm run dev
# or
bun run dev
```

## Features

### 1. File Upload Mode

Upload individual files or multiple files at once:

- **Drag and Drop**: Drag files directly onto the upload area
- **Browse**: Click to open file browser
- **Multi-select**: Select multiple files at once
- **Preview**: See file names and sizes before uploading

**Supported formats:**
- Microsoft Office: `.docx`, `.pptx`, `.xlsx`, `.doc`, `.ppt`, `.xls`
- OpenDocument: `.odt`, `.odp`, `.ods`
- Other: `.pdf`, `.rtf`

### 2. Folder Path Mode

Process entire directories by specifying local paths:

- **Input Path**: Full path to directory containing documents
- **Output Path**: Optional custom output location
- **Recursive Processing**: Toggle subdirectory scanning
- **Batch Processing**: Convert all supported files in one go

### 3. Conversion Options

Configure conversion behavior:

- **Recursive**: Process subdirectories (default: on)
- **Overwrite**: Replace existing output files (default: off)
- **Backend**: Choose MinerU processing backend
  - `pipeline`: Fast, CPU-only (default)
  - `vlm`: Vision-language model, better accuracy
  - `vllm`: GPU-accelerated inference
- **Timeout**: Maximum seconds per document (default: 300)

### 4. Real-Time Progress

Track conversion progress with live updates:

- **Progress Bar**: Visual indicator of overall completion
- **File Counter**: Current file being processed
- **Statistics**: Total, completed, and failed file counts
- **Current File**: Name of document currently converting
- **Status Messages**: Real-time status updates

### 5. Results Download

One-click download of converted files:

- **ZIP Package**: All converted Markdown files and images
- **Preserved Structure**: Maintains directory hierarchy
- **Summary Stats**: Conversion statistics and timing
- **Error Reporting**: Details of any failed conversions

## Usage Workflow

### Typical Workflow

```
1. Choose Input Method
   ├─► Upload Files (for individual documents)
   └─► Folder Path (for batch processing)

2. Configure Options
   ├─► Set recursive processing
   ├─► Choose backend
   └─► Adjust timeout if needed

3. Start Conversion
   └─► Click "Start Conversion"

4. Monitor Progress
   ├─► Watch real-time progress bar
   ├─► See current file being processed
   └─► View success/failure counts

5. Download Results
   ├─► Click "Download Results (ZIP)"
   └─► Start new conversion (optional)
```

### Example: Converting Research Papers

```
1. Select "Folder Path" mode
2. Input path: /home/user/Documents/research-papers
3. Output path: (leave empty for default)
4. Enable "Recursive" to process subdirectories
5. Select "vlm" backend for better accuracy with complex PDFs
6. Set timeout to 600 seconds for large documents
7. Click "Start Conversion"
8. Wait for completion (progress bar shows status)
9. Download results as ZIP file
```

### Example: Converting Individual Files

```
1. Select "Upload Files" mode
2. Drag and drop 5 DOCX files onto upload area
3. Review file list (shows names and sizes)
4. Keep default options (pipeline backend, 300s timeout)
5. Click "Start Conversion"
6. Monitor progress (currently processing: file3.docx)
7. See completion: 5/5 files successful
8. Download results
```

## API Endpoints

The backend exposes these REST API endpoints:

### Upload Files
```
POST /api/upload
Content-Type: multipart/form-data

Request: FormData with 'files' field
Response: { upload_id, files[], message }
```

### Create Conversion Job
```
POST /api/convert
Content-Type: application/json

Request:
{
  "input_path": "/path/to/documents",
  "output_path": "/path/to/output",  // optional
  "recursive": true,
  "overwrite": false,
  "backend": "pipeline",
  "timeout": 300
}

Response:
{
  "job_id": "uuid",
  "status": "pending",
  "input_path": "/path/to/documents",
  "output_path": "/path/to/output"
}
```

### Get Job Status
```
GET /api/jobs/{job_id}

Response:
{
  "job_id": "uuid",
  "status": "running",
  "progress": 45,
  "total_files": 10,
  "completed_files": 4,
  "failed_files": 1,
  "current_file": "document5.docx"
}
```

### Download Results
```
GET /api/jobs/{job_id}/download

Response: application/zip (ZIP file)
```

### WebSocket Progress Stream
```
WebSocket: /api/ws/{job_id}

Receives JSON messages with job status updates every second
```

## Configuration

### Environment Variables

Create `frontend/.env` for custom configuration:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000
```

### Frontend Port

Change dev server port in `frontend/vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    port: 5173,  // Change this
  },
})
```

### Backend Port

Change API server port when starting:

```bash
# Default: port 8000
uvicorn batch2md.web_api:app --port 9000
```

## Development

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

### Backend Development

```bash
# Install with development dependencies
uv sync --extra web --extra dev

# Start with auto-reload
uvicorn batch2md.web_api:app --reload

# View interactive API docs
open http://localhost:8000/docs
```

### Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── FileUpload.tsx   # File upload with drag-drop
│   │   ├── PathInput.tsx    # Path input field
│   │   ├── ConversionOptions.tsx  # Options panel
│   │   ├── ProgressTracker.tsx    # Progress display
│   │   └── ResultsView.tsx  # Results and download
│   ├── services/
│   │   └── api.ts           # API client functions
│   ├── types/
│   │   └── index.ts         # TypeScript definitions
│   ├── App.tsx              # Main application
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── index.html
├── package.json
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS config
└── tsconfig.json            # TypeScript config
```

### Adding Features

**Add a new conversion option:**

1. Update backend model in `src/batch2md/web_api.py`:
   ```python
   class ConversionRequest(BaseModel):
       new_option: bool = False
   ```

2. Update frontend type in `frontend/src/types/index.ts`:
   ```typescript
   export interface ConversionRequest {
       new_option: boolean;
   }
   ```

3. Add UI control in `frontend/src/components/ConversionOptions.tsx`

4. Pass to backend in `frontend/src/App.tsx`

## Troubleshooting

### Backend fails to start

**Error: `ModuleNotFoundError: No module named 'fastapi'`**

Solution:
```bash
uv sync --extra web
# or
pip install fastapi uvicorn python-multipart websockets
```

### Frontend fails to start

**Error: `Cannot find module 'react'`**

Solution:
```bash
cd frontend
npm install
```

### CORS errors in browser

**Error: `Access-Control-Allow-Origin`**

The backend already includes CORS middleware for `localhost:5173` and `localhost:3000`. If using a different port, update `src/batch2md/web_api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:YOUR_PORT"],
    # ...
)
```

### WebSocket connection fails

**Error: `WebSocket connection to 'ws://localhost:8000/api/ws/...' failed`**

1. Check backend is running on port 8000
2. Check firewall settings
3. Try restarting both frontend and backend

### File upload fails

**Error: `413 Payload Too Large`**

For very large files, increase the limit in backend configuration or use "Folder Path" mode instead.

### Conversion hangs

**Job stuck at "Converting..." forever**

1. Check backend logs: `logs/backend.log`
2. Increase timeout value in options
3. Try with a single file to isolate the issue
4. Ensure LibreOffice and MinerU are working:
   ```bash
   which soffice
   mineru --help
   ```

## Production Deployment

### Backend (Gunicorn + Nginx)

```bash
# Install gunicorn
pip install gunicorn

# Start with multiple workers
gunicorn batch2md.web_api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# Nginx reverse proxy
server {
    listen 80;
    server_name batch2md.example.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Frontend (Static Build)

```bash
cd frontend

# Build for production
npm run build

# Output is in frontend/dist/
# Serve with any static file server:
npx serve dist
# or deploy to Netlify, Vercel, etc.
```

## Security Considerations

⚠️ **Warning:** The current implementation is for local/development use only.

For production deployment, add:

1. **Authentication**: User login and API keys
2. **Rate Limiting**: Prevent abuse
3. **File Validation**: Strict file type and size checks
4. **Sandboxing**: Isolate conversion processes
5. **HTTPS**: Encrypt all communications
6. **Input Sanitization**: Prevent path traversal attacks

## Performance Tips

1. **Use Path Mode**: Faster than uploading files over HTTP
2. **Pipeline Backend**: Fastest option for most documents
3. **Adjust Timeout**: Increase for large/complex files
4. **Batch Size**: Process files in smaller batches if memory constrained
5. **Worker Processes**: Use multiple Gunicorn workers in production

## License

MIT License - Same as main batch2md project

## Support

- **Issues**: Report bugs at repository issues page
- **Documentation**: See main [README.md](README.md)
- **Frontend Docs**: See [frontend/README.md](frontend/README.md)
