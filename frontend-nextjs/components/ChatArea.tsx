'use client';

import { useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Message } from '@/lib/types';
import { AlertCircle, Copy, Check, AlertTriangle, BarChart3, Shield, Wrench } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
}

function getMessageType(content: string): 'error' | 'safety' | 'insufficient' | 'normal' {
  const lowerContent = content.toLowerCase();
  if (lowerContent.includes('safety') || lowerContent.includes('policy')) {
    return 'safety';
  }
  if (lowerContent.includes('cannot find') || lowerContent.includes('insufficient context')) {
    return 'insufficient';
  }
  return 'normal';
}

export function ChatArea({
  messages,
  isLoading,
  messagesEndRef,
}: ChatAreaProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const copyToClipboard = (text: string, messageId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(messageId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-8 space-y-6 flex flex-col bg-slate-950">
      {messages.length === 0 ? (
        <div className="flex-1" />
      ) : (
        messages.map((message) => {
          const messageType = message.error ? 'error' : getMessageType(message.content);
          const isLoading = message.content === 'Researching...';

          return (
            <div
              key={message.id}
              className={cn(
                'flex animate-fadeIn',
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              <div
                className={cn(
                  'max-w-2xl rounded-2xl p-4 sm:p-5 transition-all duration-200',
                  message.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-none shadow-md'
                    : messageType === 'error'
                    ? 'bg-red-900/20 border border-red-500/50 text-red-100 rounded-bl-none'
                    : messageType === 'safety'
                    ? 'bg-amber-900/20 border border-amber-500/50 text-amber-100 rounded-bl-none'
                    : messageType === 'insufficient'
                    ? 'bg-blue-900/20 border border-blue-500/30 text-blue-100 rounded-bl-none'
                    : 'bg-slate-800 text-slate-100 rounded-bl-none shadow-sm'
                )}
              >
                {message.error ? (
                  <div className="flex gap-3">
                    <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-red-300 mb-1">Error</p>
                      <p className="text-sm text-red-200">{message.error}</p>
                    </div>
                  </div>
                ) : isLoading ? (
                  <div className="flex gap-2 items-center">
                    <div className="flex gap-1">
                      <div className="h-2 w-2 bg-slate-400 rounded-full animate-bounce" />
                      <div className="h-2 w-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="h-2 w-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                    <span className="text-sm font-medium">Researching...</span>
                  </div>
                ) : (
                  <div className="relative group">
                    {/* Special message type indicators */}
                    {messageType === 'safety' && (
                      <div className="flex gap-2 mb-3 pb-3 border-b border-amber-500/30">
                        <Shield className="h-4 w-4 text-amber-500 flex-shrink-0" />
                        <span className="text-xs font-semibold text-amber-300">SAFETY NOTICE</span>
                      </div>
                    )}
                    {messageType === 'insufficient' && (
                      <div className="flex gap-2 mb-3 pb-3 border-b border-blue-500/30">
                        <AlertTriangle className="h-4 w-4 text-blue-400 flex-shrink-0" />
                        <span className="text-xs font-semibold text-blue-300">INSUFFICIENT CONTEXT</span>
                      </div>
                    )}
                    
                    {message.metadata?.tool_calls && message.metadata.tool_calls.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-3 pb-3 border-b border-indigo-500/30">
                        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-[10px] font-bold text-indigo-400 uppercase tracking-tight">
                          <Wrench className="h-2.5 w-2.5" />
                          Tools Used
                        </div>
                        {message.metadata.tool_calls.map((tc, idx) => (
                           <div key={idx} className="px-2 py-0.5 rounded-full bg-slate-700/50 border border-slate-600 text-[10px] font-medium text-slate-300">
                             {tc.tool.replace(/_/g, ' ')}
                           </div>
                        ))}
                      </div>
                    )}

                    <div className="prose prose-invert max-w-none text-sm">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          h1: ({ ...props }) => (
                            <h1 className="text-2xl font-bold mt-4 mb-3 text-slate-100" {...props} />
                          ),
                          h2: ({ ...props }) => (
                            <h2 className="text-xl font-bold mt-3 mb-2 text-slate-100" {...props} />
                          ),
                          h3: ({ ...props }) => (
                            <h3 className="text-lg font-semibold mt-2 mb-1 text-slate-200" {...props} />
                          ),
                          p: ({ ...props }) => (
                            <p className="mb-2 text-sm leading-relaxed text-inherit" {...props} />
                          ),
                          ul: ({ ...props }) => (
                            <ul className="list-disc list-inside mb-2 space-y-1 text-inherit" {...props} />
                          ),
                          ol: ({ ...props }) => (
                            <ol className="list-decimal list-inside mb-2 space-y-1 text-inherit" {...props} />
                          ),
                          li: ({ ...props }) => (
                            <li className="text-sm text-inherit" {...props} />
                          ),
                          blockquote: ({ ...props }) => (
                            <blockquote
                              className="border-l-4 border-slate-600 pl-4 italic my-2 text-slate-300"
                              {...props}
                            />
                          ),
                          table: ({ ...props }) => (
                            <div className="overflow-x-auto my-2">
                              <table className="border-collapse border border-slate-600 text-xs" {...props} />
                            </div>
                          ),
                          th: ({ ...props }) => (
                            <th className="border border-slate-600 px-2 py-1 bg-slate-700 font-semibold" {...props} />
                          ),
                          td: ({ ...props }) => (
                            <td className="border border-slate-600 px-2 py-1" {...props} />
                          ),
                          code: (props: any) => (
                            <code
                              className={cn(
                                'font-mono text-xs rounded',
                                props.inline
                                  ? 'bg-slate-700 px-2 py-0.5 text-slate-100'
                                  : 'block bg-slate-950 p-3 my-2 overflow-x-auto border border-slate-700'
                              )}
                              {...props}
                            />
                          ),
                          a: ({ ...props }) => (
                            <a className="text-blue-400 hover:text-blue-300 underline" {...props} />
                          ),
                          strong: ({ ...props }) => (
                            <strong className="font-bold text-slate-50" {...props} />
                          ),
                          em: ({ ...props }) => (
                            <em className="italic text-slate-200" {...props} />
                          ),
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>

                    {message.role === 'assistant' && !isLoading && (
                      <button
                        onClick={() => copyToClipboard(message.content, message.id)}
                        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-slate-700/50 rounded-lg"
                        title="Copy message"
                      >
                        {copiedId === message.id ? (
                          <Check className="h-4 w-4 text-green-400" />
                        ) : (
                          <Copy className="h-4 w-4 text-slate-400" />
                        )}
                      </button>
                    )}
                  </div>
                )}

                {message.sources && message.sources.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-600/50 space-y-2">
                    <p className="text-xs font-semibold text-slate-300">
                      📚 Sources:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {message.sources.map((_, index) => (
                        <span
                          key={index}
                          className="inline-block text-xs px-2.5 py-1.5 rounded-full bg-blue-600/30 border border-blue-500/30 text-blue-300 font-semibold hover:bg-blue-600/50 transition-colors cursor-pointer"
                        >
                          [{index + 1}]
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
