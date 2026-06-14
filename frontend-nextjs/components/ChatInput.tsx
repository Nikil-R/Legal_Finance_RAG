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
    <div className="bg-gradient-to-t from-background via-background/90 to-transparent pt-8 pb-4 sm:pb-6 px-4 relative z-10">
      {/* Health Warning */}
      {!isBackendHealthy && (
        <div className="max-w-3xl mx-auto mb-3 p-3 rounded-2xl bg-red-500/5 border border-red-500/20 flex gap-3 items-center animate-message">
          <AlertCircle className="h-4 w-4 text-red-500 shrink-0" />
          <p className="text-[11px] font-bold text-red-600 dark:text-red-400 uppercase tracking-tight">
            Backend Offline • Messages will fail
          </p>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative flex items-end bg-[#171717] rounded-3xl border border-border/50 focus-within:border-primary/30 shadow-lg transition-all duration-300">
        
        {/* Mobile Upload Pin */}
        <button
          onClick={(e) => { e.preventDefault(); onUploadClick?.(); }}
          className="absolute left-2 bottom-2 flex h-9 w-9 items-center justify-center rounded-full text-muted hover:text-foreground transition-colors sm:hidden"
          title="Upload document"
        >
          <Paperclip className="h-5 w-5" />
        </button>

        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isBackendHealthy ? 'Message LegalFinanceAI...' : 'System offline. Reconnecting...'}
          disabled={isLoading || !isBackendHealthy}
          rows={1}
          className={cn(
            "w-full resize-none bg-transparent pl-4 sm:pl-5 pr-[88px] py-3.5 text-[15px] focus:outline-none",
            "text-foreground placeholder:text-muted/80",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "max-h-[200px] min-h-[52px]"
          )}
        />
          
        {/* Actions inside input */}
        <div className="absolute right-2 bottom-2 flex items-center gap-1">
          {/* Voice Input Button */}
          <button
            onClick={toggleListening}
            disabled={isLoading || !isBackendHealthy}
            className={cn(
              "flex h-9 w-9 items-center justify-center rounded-full transition-all",
              isListening 
                ? "bg-red-500/20 text-red-500 animate-pulse" 
                : "text-muted hover:bg-white/5 hover:text-foreground"
            )}
            title={isListening ? "Stop listening" : "Voice input"}
          >
            {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </button>

          {/* Send Action */}
          <button
            type="submit"
            disabled={isDisabled}
            className={cn(
              "flex h-9 w-9 items-center justify-center rounded-full transition-all",
              isDisabled 
                ? "bg-[#262626] text-muted cursor-not-allowed" 
                : "bg-white text-black hover:opacity-90 active:scale-95"
            )}
          >
            {isLoading ? (
              <div className="h-4 w-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
            ) : (
              <Send className="h-4 w-4 -ml-0.5" />
            )}
          </button>
        </div>
      </form>

      <div className="max-w-3xl mx-auto text-center mt-2.5">
         <p className="text-[11px] text-muted">
           LegalFinance AI can make mistakes. Please verify important information with official sources.
         </p>
      </div>
    </div>
  );
}
