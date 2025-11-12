import { Download, CheckCircle } from 'lucide-react';
import type { ConversionJob } from '../types';
import { downloadResults } from '../services/api';

interface ResultsViewProps {
  job: ConversionJob;
  onNewConversion: () => void;
}

export default function ResultsView({ job, onNewConversion }: ResultsViewProps) {
  const handleDownload = async () => {
    try {
      await downloadResults(job.job_id);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download results. Please try again.');
    }
  };

  if (job.status !== 'completed') {
    return null;
  }

  return (
    <div className="w-full p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <div className="flex items-center justify-center mb-6">
        <CheckCircle className="h-16 w-16 text-green-500" />
      </div>

      <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-2">
        Conversion Complete!
      </h2>

      <p className="text-center text-gray-600 dark:text-gray-400 mb-6">
        Successfully converted {job.completed_files} of {job.total_files} files
      </p>

      {job.failed_files > 0 && (
        <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            ⚠ {job.failed_files} file(s) failed to convert
          </p>
        </div>
      )}

      <div className="space-y-3">
        <button
          onClick={handleDownload}
          className="w-full flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200"
        >
          <Download className="h-5 w-5 mr-2" />
          Download Results (ZIP)
        </button>

        <button
          onClick={onNewConversion}
          className="w-full px-6 py-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100 font-medium rounded-lg transition-colors duration-200"
        >
          Start New Conversion
        </button>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Conversion Summary
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Total Files:</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {job.total_files}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Successful:</span>
            <span className="font-medium text-green-600 dark:text-green-400">
              {job.completed_files}
            </span>
          </div>
          {job.failed_files > 0 && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Failed:</span>
              <span className="font-medium text-red-600 dark:text-red-400">
                {job.failed_files}
              </span>
            </div>
          )}
          {job.start_time && job.end_time && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Duration:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {calculateDuration(job.start_time, job.end_time)}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function calculateDuration(startTime: string, endTime: string): string {
  const start = new Date(startTime);
  const end = new Date(endTime);
  const durationMs = end.getTime() - start.getTime();
  const seconds = Math.floor(durationMs / 1000);
  const minutes = Math.floor(seconds / 60);

  if (minutes > 0) {
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  }
  return `${seconds}s`;
}
