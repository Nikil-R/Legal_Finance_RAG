'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, AlertCircle, Paperclip, Mic, MicOff } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  isBackendHealthy?: boolean;
  onUploadClick?: () => void;
}

export function ChatInput({
  onSend,
  isLoading,
  isBackendHealthy = true,
  onUploadClick,
}: ChatInputProps) {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize Speech Recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput((prev) => prev + (prev ? ' ' : '') + transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const toggleListening = (e: React.MouseEvent) => {
    e.preventDefault();
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      setIsListening(true);
      recognitionRef.current?.start();
    }
  };

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
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  const isDisabled = isLoading || !isBackendHealthy || !input.trim();

  return (
    <div className="border-t border-slate-100 dark:border-slate-800 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md p-4 sm:p-6 space-y-3 shadow-2xl relative z-10">
      {/* Health Warning */}
      {!isBackendHealthy && (
        <div className="p-3 rounded-2xl bg-red-500/5 border border-red-500/20 flex gap-3 items-center animate-message">
          <AlertCircle className="h-4 w-4 text-red-500 shrink-0" />
          <p className="text-[11px] font-bold text-red-600 dark:text-red-400 uppercase tracking-tight">
            Backend Offline • Messages will fail
          </p>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2 items-end max-w-5xl mx-auto">
        {/* Mobile Upload Pin */}
        <button
          onClick={(e) => { e.preventDefault(); onUploadClick?.(); }}
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-blue-500 transition-colors sm:hidden"
          title="Upload document"
        >
          <Paperclip className="h-5 w-5" />
        </button>

        <div className="flex-1 min-w-0 flex gap-2 items-end bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-800 px-2 py-1.5 focus-within:border-blue-500/50 focus-within:shadow-[0_0_0_4px_rgba(59,130,246,0.1)] transition-all duration-300">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isBackendHealthy ? 'Message LegalFinanceAI...' : 'System offline. Reconnecting...'}
            disabled={isLoading || !isBackendHealthy}
            rows={1}
            className={cn(
              "w-full resize-none bg-transparent px-3 py-1.5 text-sm font-medium focus:outline-none",
              "text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "max-h-52 min-h-[36px]"
            )}
          />
          
          {/* Voice Input Button */}
          <button
            onClick={toggleListening}
            disabled={isLoading || !isBackendHealthy}
            className={cn(
              "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-all",
              isListening 
                ? "bg-red-500 text-white animate-pulse" 
                : "text-slate-400 hover:text-blue-500"
            )}
            title={isListening ? "Stop listening" : "Voice input"}
          >
            {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </button>
        </div>

        {/* Send Action */}
        <button
          type="submit"
          disabled={isDisabled}
          className={cn(
            "flex h-11 w-11 shrink-0 items-center justify-center rounded-xl font-bold transition-all shadow-lg active:scale-95 group",
            isDisabled 
              ? "bg-slate-100 dark:bg-slate-800 text-slate-400 cursor-not-allowed" 
              : "send-button-gradient shadow-blue-500/20 text-white hover:brightness-110"
          )}
        >
          {isLoading ? (
            <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Send className="h-4 w-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          )}
        </button>
      </form>

      <div className="flex items-center justify-center gap-4 text-[10px] text-slate-400 font-bold uppercase tracking-widest leading-none pb-2">
         <span className="flex items-center gap-1"><kbd className="bg-slate-100 dark:bg-slate-800 px-1 rounded">Enter</kbd> to send</span>
         <span className="h-1 w-1 rounded-full bg-slate-200 dark:bg-slate-700" />
         <span className="flex items-center gap-1"><kbd className="bg-slate-100 dark:bg-slate-800 px-1 rounded">Shift+Enter</kbd> for line</span>
      </div>
    </div>
  );
}
