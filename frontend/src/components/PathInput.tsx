import { useState } from 'react';
import { Folder } from 'lucide-react';

interface PathInputProps {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  description?: string;
}

export default function PathInput({
  label,
  placeholder,
  value,
  onChange,
  description,
}: PathInputProps) {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {label}
      </label>

      <div
        className={`
          flex items-center border rounded-lg px-3 py-2
          transition-colors duration-200
          ${isFocused
            ? 'border-blue-500 ring-2 ring-blue-200 dark:ring-blue-800'
            : 'border-gray-300 dark:border-gray-600'
          }
        `}
      >
        <Folder className="h-5 w-5 text-gray-400 dark:text-gray-500 mr-2" />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          className="flex-1 bg-transparent outline-none text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
        />
      </div>

      {description && (
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {description}
        </p>
      )}
    </div>
  );
}
