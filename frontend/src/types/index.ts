export interface ConversionJob {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  input_path?: string;
  output_path?: string;
  error?: string;
  progress: number;
  total_files: number;
  completed_files: number;
  failed_files: number;
  current_file?: string;
  start_time?: string;
  end_time?: string;
}

export interface ConversionRequest {
  input_path?: string;
  output_path?: string;
  recursive: boolean;
  overwrite: boolean;
  backend: 'pipeline' | 'vlm' | 'vllm';
  timeout: number;
}

export interface UploadResponse {
  upload_id: string;
  files: string[];
  message: string;
}
