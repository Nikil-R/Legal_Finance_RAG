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
      isUser ? "flex-row-reverse" : "flex-row"
    )}>
      {/* Avatar */}
      <div className={cn(
        "flex h-9 w-9 shrink-0 items-center justify-center rounded-xl shadow-lg transition-transform group-hover:scale-105",
        isUser 
          ? "bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400" 
          : "bg-gradient-to-br from-blue-500 to-blue-700 text-white"
      )}>
        {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
      </div>

      {/* Message Bubble */}
      <div className={cn(
        "flex flex-col max-w-[85%] sm:max-w-[70%]",
        isUser ? "items-end" : "items-start"
      )}>
        <div className={cn(
          "relative p-4 rounded-2xl shadow-sm transition-all",
          isUser 
            ? "user-bubble-gradient text-white rounded-tr-none" 
            : "bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 text-slate-900 dark:text-white rounded-tl-none",
          isSafetyBlock && "border-amber-500/50 bg-amber-500/5 dark:bg-amber-500/5 border-l-4",
          isError && !isSafetyBlock && "border-red-500/50 bg-red-500/5 border-l-4"
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
            <div className="flex flex-wrap gap-2 mb-3 pb-3 border-b border-indigo-500/20">
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-tight">
                <Wrench className="h-2.5 w-2.5" />
                Tools Used
              </div>
              {message.metadata.tool_calls.map((tc, idx) => (
                 <div key={idx} className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-[10px] font-medium text-slate-500 dark:text-slate-400">
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

          {/* Hover Actions (Copy / Share / Download) */}
          {!isUser && !isError && (
             <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
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
                  className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors"
                  title="Download PDF"
                >
                  <Download className="h-3 w-3 text-slate-400" />
                </button>
                <button 
                  onClick={copyToClipboard}
                  className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors"
                  title="Copy response"
                >
                  {copied ? <Check className="h-3 w-3 text-green-500" /> : <Copy className="h-3 w-3 text-slate-400" />}
                </button>
             </div>
          )}
        </div>

        {/* Timestamp / Info Footer */}
        <div className="mt-1.5 flex items-center gap-2 px-1">
           <span className="text-[10px] font-medium text-slate-400 uppercase">
             {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
           </span>
           {isUser && <span className="text-[10px] font-bold text-blue-500/50 uppercase">Sent</span>}
        </div>
      </div>
    </div>
  );
}
