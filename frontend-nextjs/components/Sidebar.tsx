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
    <div className="flex flex-col h-full bg-card border-r border-border text-muted">
      {/* Sidebar Header */}
      <div className="p-6 flex items-center justify-between border-b border-border">
        <div className="flex items-center gap-2">
          <Files className="h-4 w-4 text-primary" />
          <span className="text-xs font-bold uppercase tracking-widest text-foreground">Knowledge Base</span>
        </div>
        <button onClick={onClose} className="lg:hidden p-1 hover:bg-background rounded">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8 scrollbar-hide">
        {/* Upload Hub */}
        <div className="space-y-4">
          <div
            {...getRootProps()}
            className={cn(
              "relative group overflow-hidden rounded-2xl border-2 border-dashed transition-all p-6 text-center cursor-pointer",
              isDragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-background/50",
              isUploading && "opacity-50 cursor-wait"
            )}
          >
            <input {...getInputProps()} />
            <div className="space-y-3">
              <div className="flex justify-center">
                <div className="p-3 rounded-xl bg-background text-muted group-hover:text-primary transition-colors">
                  <Upload className="h-6 w-6" />
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-bold text-foreground uppercase tracking-tight">Drop Documents</p>
                <p className="text-[10px] text-muted font-medium">PDF, DOCX, TXT • Max 50MB</p>
              </div>
            </div>
            
            {isUploading && (
              <div className="absolute inset-0 bg-[#0A0A0A]/80 backdrop-blur-sm flex items-center justify-center p-6">
                <div className="w-full space-y-3">
                  <div className="flex justify-between text-[10px] font-bold uppercase text-primary">
                    <span>Indexing...</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-background rounded-full overflow-hidden border border-border">
                    <div className="h-full bg-gradient-to-r from-primary to-primary-dark transition-all duration-300" style={{ width: `${progress}%` }} />
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
            <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted">Workspace Files</h3>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-background border border-border text-muted font-bold">{uploadedFiles.length + uploadHistory.length}</span>
          </div>

          <div className="space-y-2">
            {/* Active/History uploads */}
            {uploadHistory.map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 rounded-xl bg-background/50 border border-border">
                 <div className="flex items-center gap-3 min-w-0">
                    <FileText className={cn(
                      "h-4 w-4 shrink-0",
                      item.status === 'success' ? "text-green-500" : item.status === 'error' ? "text-red-500" : "text-primary animate-pulse"
                    )} />
                    <span className="text-[11px] font-medium text-foreground truncate">{item.name}</span>
                 </div>
                 {item.status === 'pending' && <Clock className="h-3 w-3 text-muted animate-spin" />}
                 {item.status === 'success' && <CheckCircle className="h-3 w-3 text-green-500" />}
              </div>
            ))}

            {/* Empty State */}
            {uploadedFiles.length === 0 && uploadHistory.length === 0 && (
              <div className="py-12 flex flex-col items-center justify-center border border-border rounded-2xl bg-background/20 border-dashed">
                <Inbox className="h-8 w-8 text-muted mb-3" />
                <p className="text-[10px] font-bold text-muted uppercase">No context provided</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Sidebar Footer */}
      <div className="p-6 border-t border-border space-y-4">
         <div className="flex items-center gap-3 group cursor-help">
            <div className="h-8 w-8 rounded-lg bg-background flex items-center justify-center group-hover:bg-border transition-colors border border-border">
               <HelpCircle className="h-4 w-4 text-muted" />
            </div>
            <div>
               <p className="text-[11px] font-bold text-foreground">Data Privacy</p>
               <p className="text-[9px] text-muted font-medium">Local processing only</p>
            </div>
         </div>
      </div>
    </div>
  );
}
