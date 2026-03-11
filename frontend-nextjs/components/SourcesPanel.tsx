'use client';

import { Message, Source } from '@/lib/types';
import { FileText, ExternalLink, Copy, CheckCircle } from 'lucide-react';
import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface SourcesPanelProps {
  messages: Message[];
  onSourceClick?: (source: Source) => void;
}

export function SourcesPanel({ messages, onSourceClick }: SourcesPanelProps) {
  // Extract unique sources from all assistant messages
  const uniqueSources: Map<string, Source & { count: number }> = new Map();

  messages.forEach((message) => {
    if (message.role === 'assistant' && message.sources) {
      message.sources.forEach((source) => {
        const key = `${source.reference_id || source.source}`;
        if (uniqueSources.has(key)) {
          const existing = uniqueSources.get(key)!;
          existing.count = (existing.count || 1) + 1;
        } else {
          uniqueSources.set(key, { ...source, count: 1 });
        }
      });
    }
  });

  const sources = Array.from(uniqueSources.values()).sort(
    (a, b) => (b.relevance_score || 0) - (a.relevance_score || 0)
  );

  if (sources.length === 0) {
    return null;
  }

  return (
    <aside className="hidden lg:flex w-80 border-l border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex-col h-[calc(100vh-4rem)] shadow-sm">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-slate-800 p-6 bg-gray-50 dark:bg-slate-800">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          <div>
            <h2 className="text-sm font-semibold text-gray-900 dark:text-slate-100">
              Sources & Citations
            </h2>
            <p className="text-xs text-gray-600 dark:text-slate-500">
              {sources.length} {sources.length === 1 ? 'source' : 'sources'}
            </p>
          </div>
        </div>
      </div>

      {/* Sources List */}
      <div className="flex-1 overflow-y-auto divide-y divide-gray-200 dark:divide-slate-800">
        {sources.map((source, index) => (
          <SourceCard
            key={source.reference_id || `${source.source}-${index}`}
            source={source}
            index={index + 1}
            onSourceClick={onSourceClick}
          />
        ))}
      </div>
    </aside>
  );
}

interface SourceCardProps {
  source: Source & { count?: number };
  index: number;
  onSourceClick?: (source: Source) => void;
}

function SourceCard({ source, index, onSourceClick }: SourceCardProps) {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(source.excerpt || source.source);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [source]);

  const relevancePercentage = Math.round((source.relevance_score || 0) * 100);

  return (
    <div
      className="p-4 hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors cursor-pointer group"
      onClick={() => onSourceClick?.(source)}
    >
      {/* Index Badge */}
      <div className="flex items-start gap-3 mb-3">
        <div className="flex h-7 w-7 items-center justify-center flex-shrink-0 rounded-full bg-blue-100 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20">
          <span className="text-xs font-semibold text-blue-700 dark:text-blue-400">
            {index}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          {/* Source Title */}
          <h3 className="text-sm font-medium text-gray-900 dark:text-slate-100 truncate group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
            {source.source.split('/').pop() || source.source}
          </h3>

          {/* Source Domain/Origin */}
          {source.domain && (
            <p className="text-xs text-gray-600 dark:text-slate-500 truncate">
              {source.domain}
            </p>
          )}
        </div>

        {/* Relevance Badge */}
        {source.relevance_score !== undefined && (
          <div className="flex-shrink-0 text-right">
            <p className="text-xs font-semibold text-gray-700 dark:text-slate-300">
              {relevancePercentage}%
            </p>
            <p className="text-xs text-gray-600 dark:text-slate-500">relevant</p>
          </div>
        )}
      </div>

      {/* Excerpt */}
      {source.excerpt && (
        <p className="text-xs text-gray-700 dark:text-slate-400 line-clamp-3 mb-3 leading-relaxed">
          "{source.excerpt}"
        </p>
      )}

      {/* Citation Info */}
      {source.citation_spans && source.citation_spans.length > 0 && (
        <div className="mb-3 text-xs text-gray-600 dark:text-slate-500">
          <p>
            {source.citation_spans.length}{' '}
            {source.citation_spans.length === 1 ? 'citation' : 'citations'}
          </p>
        </div>
      )}

      {/* Use Counter */}
      {(source as any).count && (source as any).count > 1 && (
        <div className="mb-3 text-xs text-gray-600 dark:text-slate-500 flex items-center gap-1">
          <CheckCircle className="h-3 w-3 text-green-600 dark:text-green-400" />
          Used in {(source as any).count} responses
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2 pt-3 border-t border-gray-200 dark:border-slate-700">
        <button
          onClick={(e) => {
            e.stopPropagation();
            copyToClipboard();
          }}
          className="flex-1 inline-flex items-center justify-center gap-1 px-2 py-1.5 text-xs font-medium text-gray-700 dark:text-slate-300 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
          title="Copy source text"
        >
          {copied ? (
            <>
              <CheckCircle className="h-3 w-3" />
              Copied
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              Copy
            </>
          )}
        </button>

        {source.origin && (
          <a
            href={source.origin}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex-1 inline-flex items-center justify-center gap-1 px-2 py-1.5 text-xs font-medium text-gray-700 dark:text-slate-300 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
            title="Open source"
          >
            <ExternalLink className="h-3 w-3" />
            Open
          </a>
        )}
      </div>
    </div>
  );
}
