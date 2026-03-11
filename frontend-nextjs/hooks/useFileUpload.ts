'use client';

import { useState, useCallback, useRef } from 'react';
import { uploadFile, ApiError } from '@/lib/api-client';
import { UploadResponse, UploadedFile } from '@/lib/types';

const ALLOWED_TYPES = [
  'application/pdf',
  'text/plain',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
];

const MAX_FILE_SIZE = 200 * 1024 * 1024; // 200MB
const ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.docx', '.doc'];

export function useFileUpload() {
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const validateFile = useCallback((file: File): string | null => {
    // Check file type by MIME type
    if (!ALLOWED_TYPES.includes(file.type)) {
      return `File type "${file.type}" is not supported. Please upload PDF, TXT, or DOCX files.`;
    }

    // Double-check extension
    const filename = file.name.toLowerCase();
    const hasValidExtension = ALLOWED_EXTENSIONS.some((ext) =>
      filename.endsWith(ext)
    );
    if (!hasValidExtension) {
      return `File extension not recognized. Please upload PDF, TXT, or DOCX files.`;
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      const sizeMB = (MAX_FILE_SIZE / (1024 * 1024)).toFixed(0);
      return `File size must be less than ${sizeMB}MB. Your file is ${(file.size / (1024 * 1024)).toFixed(1)}MB.`;
    }

    // Check file size minimum (at least 1KB)
    if (file.size < 1024) {
      return `File is too small. Please provide a file with content.`;
    }

    return null;
  }, []);

  const upload = useCallback(
    async (file: File): Promise<UploadResponse | null> => {
      setError(null);
      setProgress(0);
      setIsUploading(true);

      // Validate file
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        setIsUploading(false);
        return null;
      }

      try {
        // Simulate progress
        progressIntervalRef.current = setInterval(() => {
          setProgress((prev) => Math.min(prev + 8, 95));
        }, 200);

        console.log(`[Upload] Starting upload for file: ${file.name}`);
        const response = await uploadFile(file);

        // Clear progress interval
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
        }
        setProgress(100);

        if (!response.success) {
          const errorMsg =
            response.message || 'Upload failed. Please try again.';
          throw new ApiError(null, 'upload_error', errorMsg);
        }

        // Add to uploaded files list
        if (response.filename) {
          const uploadedFile: UploadedFile = {
            name: response.filename,
            size: file.size,
            type: file.type,
            uploadedAt: new Date(),
          };
          setUploadedFiles((prev) => [...prev, uploadedFile]);
        }

        console.log(`[Upload] Successfully uploaded: ${file.name}`);
        return response;
      } catch (err) {
        const errorMessage =
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : 'An error occurred during upload. Please try again.';
        setError(errorMessage);
        console.error(`[Upload] Error uploading ${file.name}:`, errorMessage);
        throw new ApiError(null, 'upload_error', errorMessage);
      } finally {
        setIsUploading(false);
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
        }
      }
    },
    [validateFile]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearFiles = useCallback(() => {
    setUploadedFiles([]);
  }, []);

  return {
    upload,
    isUploading,
    progress,
    error,
    uploadedFiles,
    clearError,
    clearFiles,
  };
}
