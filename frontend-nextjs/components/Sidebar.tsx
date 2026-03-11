'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useFileUpload } from '@/hooks/useFileUpload';
import {
  Upload,
  FileText,
  AlertCircle,
  X,
  CheckCircle,
  Clock,
  Files,
  Inbox,
  ShieldAlert,
  HelpCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  onClose?: () => void;
}

export function Sidebar({ onClose }: SidebarProps) {
  const { upload, isUploading, progress, error, uploadedFiles, clearError, clearFiles } = useFileUpload();
  const [localError, setLocalError] = useState<string | null>(null);
  
  const [uploadHistory, setUploadHistory] = useState<
    Array<{ name: string; status: 'success' | 'error' | 'pending'; id: string }>
  >([]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setLocalError(null);
      clearError();

      for (const file of acceptedFiles) {
        const id = Math.random().toString(36).substring(7);
        try {
          setUploadHistory((prev) => [{ name: file.name, status: 'pending', id }, ...prev]);
          await upload(file);
          setUploadHistory((prev) =>
            prev.map((item) => item.id === id ? { ...item, status: 'success' } : item)
          );
        } catch (err) {
          setUploadHistory((prev) =>
            prev.map((item) => item.id === id ? { ...item, status: 'error' } : item)
          );
          setLocalError('Upload failed. Please check backend.');
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
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
  });

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800 text-slate-400">
      {/* Sidebar Header */}
      <div className="p-6 flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Files className="h-4 w-4 text-blue-500" />
          <span className="text-xs font-bold uppercase tracking-widest text-white">Knowledge Base</span>
        </div>
        <button onClick={onClose} className="lg:hidden p-1 hover:bg-slate-800 rounded">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8 scrollbar-thin">
        {/* Upload Hub */}
        <div className="space-y-4">
          <div
            {...getRootProps()}
            className={cn(
              "relative group overflow-hidden rounded-2xl border-2 border-dashed transition-all p-6 text-center cursor-pointer",
              isDragActive ? "border-blue-500 bg-blue-500/5" : "border-slate-800 hover:border-slate-700 hover:bg-slate-800/30",
              isUploading && "opacity-50 cursor-wait"
            )}
          >
            <input {...getInputProps()} />
            <div className="space-y-3">
              <div className="flex justify-center">
                <div className="p-3 rounded-xl bg-slate-800 text-slate-400 group-hover:text-blue-500 transition-colors">
                  <Upload className="h-6 w-6" />
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-bold text-white uppercase tracking-tight">Drop Documents</p>
                <p className="text-[10px] text-slate-500 font-medium">PDF, DOCX, TXT • Max 50MB</p>
              </div>
            </div>
            
            {isUploading && (
              <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center p-6">
                <div className="w-full space-y-3">
                  <div className="flex justify-between text-[10px] font-bold uppercase text-blue-400">
                    <span>Indexing...</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 transition-all duration-300" style={{ width: `${progress}%` }} />
                  </div>
                </div>
              </div>
            )}
          </div>

          {(localError || error) && (
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 flex gap-2 animate-message">
              <ShieldAlert className="h-4 w-4 text-red-500 shrink-0" />
              <p className="text-[10px] font-medium text-red-400 leading-normal">{localError || error}</p>
            </div>
          )}
        </div>

        {/* Upload Queue / Files */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">Workspace Files</h3>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-bold">{uploadedFiles.length + uploadHistory.length}</span>
          </div>

          <div className="space-y-2">
            {/* Active/History uploads */}
            {uploadHistory.map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/50 border border-slate-800/50">
                 <div className="flex items-center gap-3 min-w-0">
                    <FileText className={cn(
                      "h-4 w-4 shrink-0",
                      item.status === 'success' ? "text-green-500" : item.status === 'error' ? "text-red-500" : "text-blue-500 animate-pulse"
                    )} />
                    <span className="text-[11px] font-medium text-slate-300 truncate">{item.name}</span>
                 </div>
                 {item.status === 'pending' && <Clock className="h-3 w-3 text-slate-500 animate-spin" />}
                 {item.status === 'success' && <CheckCircle className="h-3 w-3 text-green-500" />}
              </div>
            ))}

            {/* Empty State */}
            {uploadedFiles.length === 0 && uploadHistory.length === 0 && (
              <div className="py-12 flex flex-col items-center justify-center border border-slate-800 rounded-2xl bg-slate-800/20 border-dashed">
                <Inbox className="h-8 w-8 text-slate-700 mb-3" />
                <p className="text-[10px] font-bold text-slate-600 uppercase">No context provided</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Sidebar Footer */}
      <div className="p-6 border-t border-slate-800 space-y-4">
         <div className="flex items-center gap-3 group cursor-help">
            <div className="h-8 w-8 rounded-lg bg-slate-800 flex items-center justify-center group-hover:bg-slate-700 transition-colors">
               <HelpCircle className="h-4 w-4 text-slate-500" />
            </div>
            <div>
               <p className="text-[11px] font-bold text-slate-300">Data Privacy</p>
               <p className="text-[9px] text-slate-500 font-medium">Local processing only</p>
            </div>
         </div>
      </div>
    </div>
  );
}
