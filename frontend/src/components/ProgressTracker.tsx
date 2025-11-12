import { CheckCircle, XCircle, Loader2, FileText } from 'lucide-react';
import type { ConversionJob } from '../types';

interface ProgressTrackerProps {
  job: ConversionJob;
}

export default function ProgressTracker({ job }: ProgressTrackerProps) {
  const getStatusIcon = () => {
    switch (job.status) {
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case 'failed':
        return <XCircle className="h-6 w-6 text-red-500" />;
      case 'running':
        return <Loader2 className="h-6 w-6 text-blue-500 animate-spin" />;
      default:
        return <FileText className="h-6 w-6 text-gray-400" />;
    }
  };

  const getStatusText = () => {
    switch (job.status) {
      case 'completed':
        return 'Conversion Completed';
      case 'failed':
        return 'Conversion Failed';
      case 'running':
        return 'Converting...';
      default:
        return 'Pending';
    }
  };

  const getStatusColor = () => {
    switch (job.status) {
      case 'completed':
        return 'text-green-600 dark:text-green-400';
      case 'failed':
        return 'text-red-600 dark:text-red-400';
      case 'running':
        return 'text-blue-600 dark:text-blue-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  return (
    <div className="w-full p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      {/* Status Header */}
      <div className="flex items-center mb-6">
        {getStatusIcon()}
        <h3 className={`ml-3 text-xl font-semibold ${getStatusColor()}`}>
          {getStatusText()}
        </h3>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span>Progress</span>
          <span>{job.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              job.status === 'failed'
                ? 'bg-red-500'
                : job.status === 'completed'
                ? 'bg-green-500'
                : 'bg-blue-500'
            }`}
            style={{ width: `${job.progress}%` }}
          />
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {job.total_files}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Total Files</p>
        </div>
        <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">
            {job.completed_files}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Completed</p>
        </div>
        <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">
            {job.failed_files}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Failed</p>
        </div>
      </div>

      {/* Current File */}
      {job.current_file && job.status === 'running' && (
        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Currently processing:
          </p>
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
            {job.current_file}
          </p>
        </div>
      )}

      {/* Error Message */}
      {job.error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
          <p className="text-sm font-medium text-red-800 dark:text-red-200 mb-1">
            Error:
          </p>
          <p className="text-sm text-red-600 dark:text-red-400">{job.error}</p>
        </div>
      )}

      {/* Paths Info */}
      <div className="mt-4 space-y-2 text-sm">
        {job.input_path && (
          <div>
            <span className="text-gray-500 dark:text-gray-400">Input: </span>
            <span className="text-gray-900 dark:text-gray-100 font-mono text-xs">
              {job.input_path}
            </span>
          </div>
        )}
        {job.output_path && (
          <div>
            <span className="text-gray-500 dark:text-gray-400">Output: </span>
            <span className="text-gray-900 dark:text-gray-100 font-mono text-xs">
              {job.output_path}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
