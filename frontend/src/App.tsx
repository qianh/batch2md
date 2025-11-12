import { useState, useEffect } from 'react';
import { FileText } from 'lucide-react';
import FileUpload from './components/FileUpload';
import PathInput from './components/PathInput';
import ConversionOptions from './components/ConversionOptions';
import ProgressTracker from './components/ProgressTracker';
import ResultsView from './components/ResultsView';
import { uploadFiles, createConversionJob, connectWebSocket } from './services/api';
import type { ConversionJob, ConversionRequest } from './types';

type InputMode = 'upload' | 'path';

function App() {
  // Input mode
  const [inputMode, setInputMode] = useState<InputMode>('upload');

  // File upload state
  const [uploadedFiles, setUploadedFiles] = useState<FileList | null>(null);
  const [uploadId, setUploadId] = useState<string>('');

  // Path input state
  const [inputPath, setInputPath] = useState('');
  const [outputPath, setOutputPath] = useState('');

  // Conversion options
  const [recursive, setRecursive] = useState(true);
  const [overwrite, setOverwrite] = useState(false);
  const [backend, setBackend] = useState<'pipeline' | 'vlm' | 'vllm'>('pipeline');
  const [timeout, setTimeout] = useState(300);

  // Job state
  const [currentJob, setCurrentJob] = useState<ConversionJob | null>(null);
  const [isConverting, setIsConverting] = useState(false);

  // WebSocket connection
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  const handleFilesSelected = (files: FileList) => {
    setUploadedFiles(files);
  };

  const handleStartConversion = async () => {
    try {
      setIsConverting(true);

      let conversionInputPath = '';

      if (inputMode === 'upload') {
        // Upload files first
        if (!uploadedFiles || uploadedFiles.length === 0) {
          alert('Please select files to upload');
          setIsConverting(false);
          return;
        }

        const uploadResponse = await uploadFiles(uploadedFiles);
        setUploadId(uploadResponse.upload_id);
        conversionInputPath = uploadResponse.upload_id; // Use upload_id as path for now

        // In production, backend should handle upload_id -> path mapping
        alert('File upload completed! However, path-based conversion is recommended for local files.');
        setIsConverting(false);
        return;
      } else {
        // Use provided path
        if (!inputPath) {
          alert('Please enter an input path');
          setIsConverting(false);
          return;
        }
        conversionInputPath = inputPath;
      }

      // Create conversion request
      const request: ConversionRequest = {
        input_path: conversionInputPath,
        output_path: outputPath || undefined,
        recursive,
        overwrite,
        backend,
        timeout,
      };

      // Start conversion job
      const job = await createConversionJob(request);
      setCurrentJob(job);

      // Connect to WebSocket for progress updates
      const websocket = connectWebSocket(
        job.job_id,
        (data) => {
          setCurrentJob(data);
          if (data.status === 'completed' || data.status === 'failed') {
            setIsConverting(false);
          }
        },
        (error) => {
          console.error('WebSocket error:', error);
        },
        () => {
          console.log('WebSocket closed');
        }
      );

      setWs(websocket);
    } catch (error) {
      console.error('Conversion failed:', error);
      alert('Failed to start conversion. Please check your input and try again.');
      setIsConverting(false);
    }
  };

  const handleNewConversion = () => {
    setCurrentJob(null);
    setIsConverting(false);
    setUploadedFiles(null);
    setUploadId('');
    if (ws) {
      ws.close();
      setWs(null);
    }
  };

  const canStartConversion = () => {
    if (inputMode === 'upload') {
      return uploadedFiles && uploadedFiles.length > 0;
    }
    return inputPath.trim() !== '';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <FileText className="h-12 w-12 text-blue-600 dark:text-blue-400" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Batch2MD
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Convert documents to Markdown using LibreOffice and MinerU
          </p>
        </div>

        {/* Show results if conversion is complete */}
        {currentJob && currentJob.status === 'completed' ? (
          <ResultsView job={currentJob} onNewConversion={handleNewConversion} />
        ) : currentJob && isConverting ? (
          /* Show progress tracker during conversion */
          <ProgressTracker job={currentJob} />
        ) : (
          /* Show conversion form */
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8">
            {/* Input Mode Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Input Method
              </label>
              <div className="flex space-x-4">
                <button
                  onClick={() => setInputMode('upload')}
                  className={`flex-1 px-4 py-3 rounded-lg font-medium transition-colors duration-200 ${
                    inputMode === 'upload'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  Upload Files
                </button>
                <button
                  onClick={() => setInputMode('path')}
                  className={`flex-1 px-4 py-3 rounded-lg font-medium transition-colors duration-200 ${
                    inputMode === 'path'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  Folder Path
                </button>
              </div>
            </div>

            {/* Input Section */}
            <div className="mb-6">
              {inputMode === 'upload' ? (
                <FileUpload onFilesSelected={handleFilesSelected} />
              ) : (
                <PathInput
                  label="Input Directory Path"
                  placeholder="/path/to/documents"
                  value={inputPath}
                  onChange={setInputPath}
                  description="Enter the full path to the directory containing documents"
                />
              )}
            </div>

            {/* Output Path */}
            <div className="mb-6">
              <PathInput
                label="Output Directory Path (Optional)"
                placeholder="/path/to/output or leave empty for default"
                value={outputPath}
                onChange={setOutputPath}
                description="Leave empty to create 'markdown' folder in input directory"
              />
            </div>

            {/* Conversion Options */}
            <div className="mb-6">
              <ConversionOptions
                recursive={recursive}
                onRecursiveChange={setRecursive}
                overwrite={overwrite}
                onOverwriteChange={setOverwrite}
                backend={backend}
                onBackendChange={setBackend}
                timeout={timeout}
                onTimeoutChange={setTimeout}
              />
            </div>

            {/* Start Button */}
            <button
              onClick={handleStartConversion}
              disabled={!canStartConversion() || isConverting}
              className={`w-full px-6 py-4 rounded-lg font-semibold text-lg transition-colors duration-200 ${
                canStartConversion() && !isConverting
                  ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
                  : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
              }`}
            >
              {isConverting ? 'Starting Conversion...' : 'Start Conversion'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
