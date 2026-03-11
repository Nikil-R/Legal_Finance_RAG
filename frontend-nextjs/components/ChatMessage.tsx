'use client';

import { Message, Source } from '@/lib/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check, AlertCircle } from 'lucide-react';
import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
  message: Message;
  onSourceClick?: (source: Source) => void;
}

export function ChatMessage({ message, onSourceClick }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [message.content]);

  const isUser = message.role === 'user';
  const isError = !!message.error;

  if (isError) {
    return (
      <div className="flex gap-4 mb-4 animate-in fade-in slide-in-from-bottom-2">
        <div className="flex-shrink-0 flex h-8 w-8 items-center justify-center rounded-lg bg-red-100 dark:bg-red-500/10">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
        </div>
        <div className="flex-grow">
          <div className="rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 p-4">
            <p className="text-sm font-medium text-red-900 dark:text-red-300 mb-1">
              {message.isSafetyBlock ? '🚫 Safety Block' : '⚠️ Error'}
            </p>
            <p className="text-sm text-red-800 dark:text-red-200">
              {message.error}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn('flex gap-4 mb-4 animate-in fade-in slide-in-from-bottom-2', {
        'justify-end': isUser,
      })}
    >
      {/* Avatar */}
      {!isUser && (
        <div className="flex-shrink-0 flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-500/10">
          <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">
            AI
          </span>
        </div>
      )}

      {/* Message Content */}
      <div className={cn('flex-grow', { 'max-w-xs md:max-w-md': isUser })}>
        <div
          className={cn(
            'rounded-lg p-4 transition-colors',
            isUser
              ? 'bg-blue-600 dark:bg-blue-600 text-white ml-auto'
              : 'bg-gray-100 dark:bg-slate-800 text-gray-900 dark:text-slate-100'
          )}
        >
          {/* Message Text */}
          <div
            className={cn('prose prose-sm dark:prose-invert max-w-none', {
              'prose-headings:text-white prose-strong:text-white prose-code:text-white':
                isUser,
            })}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>

          {/* Timestamp */}
          <p
            className={cn('text-xs mt-2 opacity-70', {
              'text-blue-100': isUser,
              'text-gray-600 dark:text-slate-500': !isUser,
            })}
          >
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        </div>

        {/* Copy Button for AI Messages */}
        {!isUser && (
          <div className="mt-2 flex justify-end">
            <button
              onClick={copyToClipboard}
              className="text-xs text-gray-600 dark:text-slate-500 hover:text-gray-900 dark:hover:text-slate-300 transition-colors flex items-center gap-1"
              title="Copy message"
            >
              {copied ? (
                <>
                  <Check className="h-3 w-3" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  Copy
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="flex-shrink-0 flex h-8 w-8 items-center justify-center rounded-lg bg-gray-300 dark:bg-slate-600">
          <span className="text-xs font-semibold text-gray-700 dark:text-slate-300">
            U
          </span>
        </div>
      )}
    </div>
  );
}

/* Markdown Component Styling */
const markdownComponents = {
  h1: ({ node, ...props }: any) => (
    <h1 className="text-xl font-bold mt-4 mb-2" {...props} />
  ),
  h2: ({ node, ...props }: any) => (
    <h2 className="text-lg font-bold mt-3 mb-2" {...props} />
  ),
  h3: ({ node, ...props }: any) => (
    <h3 className="text-base font-bold mt-2 mb-1" {...props} />
  ),
  p: ({ node, ...props }: any) => <p className="mb-2 leading-relaxed" {...props} />,
  ul: ({ node, ...props }: any) => <ul className="list-disc pl-4 mb-2" {...props} />,
  ol: ({ node, ...props }: any) => <ol className="list-decimal pl-4 mb-2" {...props} />,
  li: ({ node, ...props }: any) => <li className="mb-1" {...props} />,
  code: ({ node, inline, ...props }: any) =>
    inline ? (
      <code className="bg-opacity-20 px-1.5 py-0.5 rounded text-sm font-mono" {...props} />
    ) : (
      <code className="block bg-opacity-20 p-3 rounded-lg font-mono text-sm mb-2 overflow-x-auto" {...props} />
    ),
  blockquote: ({ node, ...props }: any) => (
    <blockquote className="border-l-4 pl-4 italic opacity-75 mb-2" {...props} />
  ),
  a: ({ node, ...props }: any) => (
    <a className="text-blue-600 dark:text-blue-400 hover:underline" {...props} />
  ),
};
