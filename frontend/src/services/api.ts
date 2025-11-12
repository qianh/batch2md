import axios from 'axios';
import type { ConversionJob, ConversionRequest, UploadResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadFiles = async (files: FileList): Promise<UploadResponse> => {
  const formData = new FormData();
  Array.from(files).forEach((file) => {
    formData.append('files', file);
  });

  const response = await api.post<UploadResponse>('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const createConversionJob = async (
  request: ConversionRequest
): Promise<ConversionJob> => {
  const response = await api.post<ConversionJob>('/api/convert', request);
  return response.data;
};

export const getJobStatus = async (jobId: string): Promise<ConversionJob> => {
  const response = await api.get<ConversionJob>(`/api/jobs/${jobId}`);
  return response.data;
};

export const downloadResults = async (jobId: string): Promise<void> => {
  const response = await api.get(`/api/jobs/${jobId}/download`, {
    responseType: 'blob',
  });

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `batch2md_results_${jobId}.zip`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const connectWebSocket = (
  jobId: string,
  onMessage: (data: ConversionJob) => void,
  onError?: (error: Event) => void,
  onClose?: () => void
): WebSocket => {
  const wsUrl = API_BASE_URL.replace('http', 'ws');
  const ws = new WebSocket(`${wsUrl}/api/ws/${jobId}`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  if (onError) {
    ws.onerror = onError;
  }

  if (onClose) {
    ws.onclose = onClose;
  }

  return ws;
};
