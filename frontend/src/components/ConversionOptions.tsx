import { Settings } from 'lucide-react';

interface ConversionOptionsProps {
  recursive: boolean;
  onRecursiveChange: (value: boolean) => void;
  overwrite: boolean;
  onOverwriteChange: (value: boolean) => void;
  backend: 'pipeline' | 'vlm' | 'vllm';
  onBackendChange: (value: 'pipeline' | 'vlm' | 'vllm') => void;
  timeout: number;
  onTimeoutChange: (value: number) => void;
}

export default function ConversionOptions({
  recursive,
  onRecursiveChange,
  overwrite,
  onOverwriteChange,
  backend,
  onBackendChange,
  timeout,
  onTimeoutChange,
}: ConversionOptionsProps) {
  return (
    <div className="w-full p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <div className="flex items-center mb-4">
        <Settings className="h-5 w-5 text-gray-600 dark:text-gray-400 mr-2" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          Conversion Options
        </h3>
      </div>

      <div className="space-y-4">
        {/* Recursive checkbox */}
        <label className="flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={recursive}
            onChange={(e) => onRecursiveChange(e.target.checked)}
            className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
            Process subdirectories recursively
          </span>
        </label>

        {/* Overwrite checkbox */}
        <label className="flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={overwrite}
            onChange={(e) => onOverwriteChange(e.target.checked)}
            className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
            Overwrite existing files
          </span>
        </label>

        {/* Backend selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            MinerU Backend
          </label>
          <select
            value={backend}
            onChange={(e) =>
              onBackendChange(e.target.value as 'pipeline' | 'vlm' | 'vllm')
            }
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="pipeline">Pipeline (Fast, CPU)</option>
            <option value="vlm">VLM (Better accuracy, slower)</option>
            <option value="vllm">VLLM (GPU accelerated)</option>
          </select>
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Choose the processing backend for PDF to Markdown conversion
          </p>
        </div>

        {/* Timeout input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Timeout (seconds)
          </label>
          <input
            type="number"
            min="60"
            max="3600"
            value={timeout}
            onChange={(e) => onTimeoutChange(parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Maximum time to wait for each document conversion
          </p>
        </div>
      </div>
    </div>
  );
}
