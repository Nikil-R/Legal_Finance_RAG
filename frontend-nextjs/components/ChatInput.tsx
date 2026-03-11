'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, AlertCircle, Loader } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  isBackendHealthy?: boolean;
}

export function ChatInput({
  onSend,
  isLoading,
  isBackendHealthy = true,
}: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-grow textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = Math.min(textareaRef.current.scrollHeight, 200);
      textareaRef.current.style.height = `${scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isLoading || !isBackendHealthy) {
      return;
    }

    onSend(input);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Ctrl+Enter or Cmd+Enter
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  const isDisabled = isLoading || !isBackendHealthy || !input.trim();

  return (
    <div className="border-t border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 sm:p-6 space-y-3 shadow-sm">
      {/* Health Warning */}
      {!isBackendHealthy && (
        <div className="p-3 rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 flex gap-2 items-start">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1 text-sm">
            <p className="font-medium text-red-900 dark:text-red-300">
              Backend Unavailable
            </p>
            <p className="text-xs text-red-800 dark:text-red-200 mt-1">
              The API server is not responding. Please ensure the backend is running.
            </p>
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2 sm:gap-3 items-end">
        <div className="flex-1 min-w-0">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isBackendHealthy
                ? 'Ask a question... (Ctrl+Enter to send)'
                : 'Backend unavailable...'
            }
            disabled={isLoading || !isBackendHealthy}
            rows={1}
            className={cn(
              'w-full resize-none rounded-lg border bg-white dark:bg-slate-800 px-4 py-3 text-sm font-medium transition-colors',
              'border-gray-300 dark:border-slate-600 text-gray-900 dark:text-slate-100',
              'placeholder:text-gray-500 dark:placeholder:text-slate-500',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
              'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-100 dark:disabled:bg-slate-800'
            )}
            style={{ maxHeight: '200px' }}
          />
        </div>

        {/* Send Button */}
        <Button
          type="submit"
          disabled={isDisabled}
          size="lg"
          className={cn(
            'gap-2 flex-shrink-0 transition-all',
            isDisabled
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:shadow-md active:scale-95'
          )}
          title={
            !isBackendHealthy
              ? 'Backend is not available'
              : isLoading
                ? 'Waiting for response...'
                : 'Send message (Ctrl+Enter)'
          }
        >
          {isLoading ? (
            <Loader className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
          <span className="hidden sm:inline">Send</span>
        </Button>
      </form>

      {/* Help Text */}
      <div className="text-xs text-gray-600 dark:text-slate-500 text-center">
        <span className="opacity-70">
          💡 Tip: Press Ctrl+Enter (or Cmd+Enter) to send
        </span>
      </div>
    </div>
  );
}
