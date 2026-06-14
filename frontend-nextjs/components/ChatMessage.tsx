'use client';

import { Message, Source } from '@/lib/types';
import { Copy, Check, AlertCircle, Bot, User, Share2, Wrench, Download } from 'lucide-react';
import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { useToast } from './ToastProvider';
import { MarkdownRenderer } from './MarkdownRenderer';

interface ChatMessageProps {
  message: Message;
  onCitationClick?: (citationNumber: number) => void;
}

export function ChatMessage({ message, onCitationClick }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const { addToast } = useToast();

  const copyToClipboard = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      addToast({
        message: 'Response copied to clipboard',
        type: 'success',
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [message.content, addToast]);

  const isUser = message.role === 'user';
  const isError = !!message.error;
  const isSafetyBlock = message.isSafetyBlock;

  return (
    <div className={cn(
      "group flex gap-4 w-full animate-message",
      isUser ? "justify-end" : "flex-row"
    )}>
      {/* Avatar (AI Only) */}
      {!isUser && (
        <div className={cn(
          "flex h-8 w-8 shrink-0 mt-1 items-center justify-center rounded-full shadow-lg",
          "bg-gradient-to-br from-primary to-primary-dark text-[#0A0A0A] shadow-primary/20"
        )}>
          <Bot className="h-5 w-5" />
        </div>
      )}

      {/* Message Bubble/Content */}
      <div className={cn(
        "flex flex-col min-w-0",
        isUser ? "w-full items-end" : "w-full items-start"
      )}>
        <div className={cn(
          "relative transition-all",
          isUser 
            ? "bg-card border border-border text-foreground rounded-3xl px-5 py-3 shadow-sm inline-block max-w-[85%] sm:max-w-[70%]" 
            : "text-foreground w-full py-1",
          isSafetyBlock && "border-amber-500/50 bg-amber-500/5 border-l-4 p-4 rounded-xl",
          isError && !isSafetyBlock && "border-red-500/50 bg-red-500/5 border-l-4 p-4 rounded-xl"
        )}>
          {/* Safety/Error Header */}
          {(isError || isSafetyBlock) && (
            <div className="flex items-center gap-2 mb-2 text-[10px] font-bold uppercase tracking-wider">
               {isSafetyBlock ? (
                 <>
                   <AlertCircle className="h-3 w-3 text-amber-500" />
                   <span className="text-amber-600 dark:text-amber-400">Compliance Warning / Policy Block</span>
                 </>
               ) : (
                 <>
                   <AlertCircle className="h-3 w-3 text-red-500" />
                   <span className="text-red-600 dark:text-red-400">System Error</span>
                 </>
               )}
            </div>
          )}

          {/* Tool Calls Indicator */}
          {!isUser && message.metadata?.tool_calls && message.metadata.tool_calls.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3 pb-3 border-b border-primary/20">
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-primary/10 border border-primary/20 text-[10px] font-bold text-primary uppercase tracking-tight">
                <Wrench className="h-2.5 w-2.5" />
                Tools Used
              </div>
              {message.metadata.tool_calls.map((tc, idx) => (
                 <div key={idx} className="px-2 py-0.5 rounded-full bg-background border border-border text-[10px] font-medium text-muted">
                   {tc.tool.replace(/_/g, ' ')}
                 </div>
              ))}
            </div>
          )}

          <div className="text-sm leading-relaxed overflow-hidden">
            {isUser ? (
              <p className="whitespace-pre-wrap">{message.content}</p>
            ) : (
              <MarkdownRenderer 
                content={message.content} 
                onCitationClick={onCitationClick}
              />
            )}
          </div>
        </div>

        {/* Hover Actions (Copy / Share / Download) & Footer */}
        <div className="mt-2 flex items-center justify-between w-full">
           <div className="flex items-center gap-2">
             {!isUser && !isError && (
                <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                   <button 
                     onClick={copyToClipboard}
                     className="p-1.5 hover:bg-card rounded-md transition-colors"
                     title="Copy response"
                   >
                     {copied ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5 text-muted" />}
                   </button>
                   <button 
                     onClick={() => {
                       import('@/lib/api-client').then(({ exportQuery }) => {
                         exportQuery(
                           message.metadata?.question || '',
                           message.content,
                           message.sources || [],
                           localStorage.getItem('chat_session_id') || ''
                         ).catch(err => console.error('Export failed', err));
                       });
                     }}
                     className="p-1.5 hover:bg-card rounded-md transition-colors"
                     title="Download PDF"
                   >
                     <Download className="h-3.5 w-3.5 text-muted" />
                   </button>
                </div>
             )}
           </div>
           
           <div className="flex items-center gap-2 px-1">
             <span className="text-[10px] font-medium text-muted uppercase">
               {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
             </span>
             {isUser && <span className="text-[10px] font-bold text-primary/50 uppercase">Sent</span>}
           </div>
        </div>
      </div>
    </div>
  );
}
