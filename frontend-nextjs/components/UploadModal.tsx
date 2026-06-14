import { useState, useRef } from 'react';
import { UploadCloud, X, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function UploadModal({ isOpen, onClose }: UploadModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [domain, setDomain] = useState<string>('tax');
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== 'application/pdf') {
        setStatus('error');
        setMessage('Only PDF files are supported.');
        return;
      }
      setFile(selectedFile);
      setStatus('idle');
      setMessage('');
    }
  };

  const pollIngestionStatus = async (jobId: string) => {
    setStatus('processing');
    setMessage('Document is being vectorized and indexed...');
    
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/v2/documents/ingest/jobs/${jobId}`);
        const data = await res.json();
        
        if (data.status === 'completed') {
          clearInterval(interval);
          setStatus('success');
          setMessage('Document successfully added to the Knowledge Base!');
          setTimeout(() => {
            onClose();
            setFile(null);
            setStatus('idle');
            setMessage('');
          }, 3000);
        } else if (data.status === 'failed') {
          clearInterval(interval);
          setStatus('error');
          setMessage('Failed to process document.');
        }
      } catch (err) {
        clearInterval(interval);
        setStatus('error');
        setMessage('Error checking ingestion status.');
      }
    }, 2000);
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus('uploading');
    setMessage('Uploading document...');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('domain', domain);

    try {
      const res = await fetch('/api/v2/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error('Upload failed');
      }

      const data = await res.json();
      if (data.job_id) {
        pollIngestionStatus(data.job_id);
      } else {
        throw new Error('No job ID returned');
      }
    } catch (err) {
      setStatus('error');
      setMessage(err instanceof Error ? err.message : 'Upload failed');
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in">
      <div className="bg-[#111827] border border-border rounded-2xl w-full max-w-md shadow-2xl overflow-hidden relative">
        <button 
          onClick={() => {
             onClose();
             setFile(null);
             setStatus('idle');
             setMessage('');
          }}
          className="absolute top-4 right-4 text-muted hover:text-foreground transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="p-6">
          <h2 className="text-xl font-bold text-foreground mb-1">Upload Document</h2>
          <p className="text-sm text-muted mb-6">Add a PDF to the LegalFinance Knowledge Base.</p>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase text-muted mb-2 tracking-wider">Domain</label>
              <select 
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full bg-[#1F2937] border border-border rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary/50 text-foreground"
                disabled={status !== 'idle' && status !== 'error'}
              >
                <option value="tax">Tax</option>
                <option value="legal">Legal</option>
                <option value="finance">Finance</option>
                <option value="general">General</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase text-muted mb-2 tracking-wider">File</label>
              
              <div 
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                  file ? 'border-primary/50 bg-primary/5' : 'border-border hover:border-muted hover:bg-[#1F2937]'
                } ${(status !== 'idle' && status !== 'error') ? 'opacity-50 pointer-events-none' : ''}`}
              >
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileChange} 
                  accept="application/pdf" 
                  className="hidden" 
                />
                <UploadCloud className={`h-10 w-10 mx-auto mb-3 ${file ? 'text-primary' : 'text-muted'}`} />
                {file ? (
                  <p className="text-sm font-medium text-primary truncate px-4">{file.name}</p>
                ) : (
                  <div>
                    <p className="text-sm font-medium text-foreground">Click to browse or drag and drop</p>
                    <p className="text-xs text-muted mt-1">PDF files only (max 10MB)</p>
                  </div>
                )}
              </div>
            </div>

            {message && (
              <div className={`p-3 rounded-xl flex items-start gap-3 text-sm ${
                status === 'error' ? 'bg-red-500/10 text-red-500 border border-red-500/20' : 
                status === 'success' ? 'bg-green-500/10 text-green-500 border border-green-500/20' :
                'bg-blue-500/10 text-blue-400 border border-blue-500/20'
              }`}>
                {status === 'error' && <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />}
                {status === 'success' && <CheckCircle className="h-4 w-4 mt-0.5 shrink-0" />}
                {(status === 'uploading' || status === 'processing') && <Loader2 className="h-4 w-4 mt-0.5 animate-spin shrink-0" />}
                <p>{message}</p>
              </div>
            )}
          </div>
        </div>

        <div className="p-6 bg-[#1F2937]/50 border-t border-border flex justify-end gap-3">
          <Button 
            variant="ghost" 
            onClick={() => {
               onClose();
               setFile(null);
               setStatus('idle');
               setMessage('');
            }}
            disabled={status === 'uploading' || status === 'processing'}
            className="text-muted hover:text-foreground hover:bg-[#2A374A]"
          >
            Cancel
          </Button>
          <Button 
            onClick={handleUpload}
            disabled={!file || status === 'uploading' || status === 'processing'}
            className="bg-primary text-black hover:bg-primary/90 font-semibold shadow-lg shadow-primary/20"
          >
            {(status === 'uploading' || status === 'processing') ? 'Processing...' : 'Upload & Ingest'}
          </Button>
        </div>
      </div>
    </div>
  );
}
