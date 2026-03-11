'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useFileUpload } from '@/hooks/useFileUpload';
import {
  Upload,
  FileText,
  AlertCircle,
  X,
  CheckCircle,
  Clock,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';

export function Sidebar() {
  const { upload, isUploading, progress, error, uploadedFiles, clearError, clearFiles } =
    useFileUpload();
  const [localError, setLocalError] = useState<string | null>(null);
  const [uploadHistory, setUploadHistory] = useState<
    Array<{ name: string; status: 'success' | 'error' | 'pending' }>
  >([]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setLocalError(null);
      clearError();

      if (acceptedFiles.length === 0) {
        setLocalError('No valid files selected');
        return;
      }

      for (const file of acceptedFiles) {
        try {
          setUploadHistory((prev) => [
            ...prev,
            { name: file.name, status: 'pending' },
          ]);

          await upload(file);

          setUploadHistory((prev) =>
            prev.map((item) =>
              item.name === file.name ? { ...item, status: 'success' } : item
            )
          );
        } catch (err) {
          const errorMsg =
            err instanceof Error ? err.message : 'Upload failed';
          setUploadHistory((prev) =>
            prev.map((item) =>
              item.name === file.name ? { ...item, status: 'error' } : item
            )
          );
          setLocalError(errorMsg);
        }
      }
    },
    [upload, clearError]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled: isUploading,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [
        '.docx',
      ],
      'application/msword': ['.doc'],
    },
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <aside className="w-64 border-r border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 flex flex-col overflow-y-auto h-[calc(100vh-4rem)] shadow-sm">
      {/* Welcome Section */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 dark:text-slate-100">
          Documents
        </h2>
        <p className="text-xs text-gray-600 dark:text-slate-500 mt-1">
          Upload PDFs, TXT, or DOCX files
        </p>
      </div>

      {/* Upload Zone */}
      <div className="mb-8">
        <div
          {...getRootProps()}
          className={cn(
            'rounded-lg border-2 border-dashed p-6 text-center transition-all cursor-pointer',
            isDragActive
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-500/10'
              : 'border-gray-300 dark:border-slate-600 hover:border-gray-400 dark:hover:border-slate-500',
            isUploading && 'opacity-50 cursor-not-allowed',
            error && 'border-red-300 dark:border-red-500/30'
          )}
        >
          <input {...getInputProps()} />

          {isDragActive ? (
            <div className="space-y-2">
              <Upload className="h-6 w-6 text-blue-500 mx-auto" />
              <p className="text-sm font-medium text-blue-600 dark:text-blue-400">
                Drop files here
              </p>
            </div>
          ) : isUploading ? (
            <div className="space-y-3">
              <div className="inline-block">
                <div className="relative h-12 w-12">
                  <svg
                    className="h-12 w-12 text-blue-600 dark:text-blue-400 animate-spin"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                </div>
              </div>
              <p className="text-sm font-medium text-gray-700 dark:text-slate-300">
                Uploading...
              </p>
              <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-xs font-medium text-gray-600 dark:text-slate-400">
                {progress}%
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              <Upload className="h-6 w-6 text-gray-400 dark:text-slate-400 mx-auto" />
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-slate-300">
                  Drag & drop files here
                </p>
                <p className="text-xs text-gray-600 dark:text-slate-500 mt-1">
                  PDF, TXT, or DOCX • Max 200MB
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Error Messages */}
        {(localError || error) && (
          <div className="mt-3 p-3 rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 flex gap-2">
            <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-xs text-red-700 dark:text-red-300">
                {localError || error}
              </p>
            </div>
            <button
              onClick={() => {
                setLocalError(null);
                clearError();
              }}
              className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>

      {/* Upload History */}
      {uploadHistory.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-slate-100">
              Upload Status
            </h3>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 text-xs"
              onClick={() => {
                setUploadHistory([]);
                clearFiles();
              }}
            >
              Clear
            </Button>
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {uploadHistory.map((item) => (
              <div
                key={item.name}
                className={cn(
                  'flex items-start gap-2 p-2 rounded-lg text-xs transition-colors',
                  item.status === 'success'
                    ? 'bg-green-50 dark:bg-green-500/10 border border-green-200 dark:border-green-500/30'
                    : item.status === 'error'
                      ? 'bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30'
                      : 'bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/30'
                )}
              >
                {item.status === 'success' ? (
                  <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                ) : item.status === 'error' ? (
                  <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                ) : (
                  <Clock className="h-4 w-4 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5 animate-spin" />
                )}
                <div className="flex-1 min-w-0">
                  <p
                    className={cn(
                      'font-medium truncate',
                      item.status === 'success'
                        ? 'text-green-700 dark:text-green-300'
                        : item.status === 'error'
                          ? 'text-red-700 dark:text-red-300'
                          : 'text-yellow-700 dark:text-yellow-300'
                    )}
                  >
                    {item.name}
                  </p>
                  <p
                    className={cn(
                      'text-xs truncate',
                      item.status === 'success'
                        ? 'text-green-600 dark:text-green-400'
                        : item.status === 'error'
                          ? 'text-red-600 dark:text-red-400'
                          : 'text-yellow-600 dark:text-yellow-400'
                    )}
                  >
                    {item.status === 'success'
                      ? 'Successfully uploaded'
                      : item.status === 'error'
                        ? 'Upload failed'
                        : 'Uploading...'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-slate-100 mb-3">
            Documents ({uploadedFiles.length})
          </h3>
          <div className="space-y-2">
            {uploadedFiles.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-start gap-2 p-3 rounded-lg bg-gray-100 dark:bg-slate-800"
              >
                <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-gray-900 dark:text-slate-300 truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-gray-600 dark:text-slate-500">
                    {formatFileSize(file.size)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Section */}
      <div className="mt-auto pt-6 border-t border-gray-200 dark:border-slate-800">
        <p className="text-xs text-gray-600 dark:text-slate-500 leading-relaxed">
          Upload documents to provide context for more accurate and relevant
          answers to your questions.
        </p>
      </div>
    </aside>
  );
}
