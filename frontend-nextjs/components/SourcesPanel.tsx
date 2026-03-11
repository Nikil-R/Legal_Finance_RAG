'use client';

import { Message, Source } from '@/lib/types';
import { FileText, X, ChevronRight, FileOutput, FileArchive, FileInput } from 'lucide-react';
import { useState, useCallback, useMemo } from 'react';
import { cn } from '@/lib/utils';
import { useToast } from './ToastProvider';

interface SourcesPanelProps {
  messages: Message[];
  onClose?: () => void;
  isOpen?: boolean;
}

export function SourcesPanel({ messages, onClose, isOpen = true }: SourcesPanelProps) {
  // Get the latest assistant message with sources
  const latestMessage = useMemo(() => {
    return [...messages].reverse().find(
      (m) => m.role === 'assistant' && (m.sources?.length ?? 0) > 0
    );
  }, [messages]);

  const sources = latestMessage?.sources || [];

  if (sources.length === 0 || !isOpen) {
    return null;
  }

  return (
    <aside className={cn(
      "w-80 border-l border-white/10 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md flex flex-col h-full shadow-lg sticky top-0 right-0 z-30 transition-all duration-300",
      "lg:flex hidden" // Responsive hide handled by parent layout mostly, but explicit here too
    )}>
      {/* Header */}
      <div className="border-b border-white/10 p-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-500/20">
            <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
              Citations
            </h2>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              {sources.length} document{sources.length === 1 ? '' : 's'} linked
            </p>
          </div>
        </div>
        <button 
          onClick={onClose}
          className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
          aria-label="Close sources panel"
        >
          <X className="h-4 w-4 text-slate-500" />
        </button>
      </div>

      {/* Sources List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {sources.map((source: Source, index: number) => (
          <SourceCard
            key={source.reference_id || `${source.source}-${index}`}
            source={source}
            index={index + 1}
          />
        ))}
      </div>
    </aside>
  );
}

interface SourceCardProps {
  source: Source;
  index: number;
}

function SourceCard({ source, index }: SourceCardProps) {
  const [expanded, setExpanded] = useState(false);
  const relevancePercentage = Math.round((source.relevance_score || 0) * 100);
  const fileName = source.source.split('/').pop() || source.source;
  
  const fileIcon = useMemo(() => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <FileOutput className="h-3.5 w-3.5 text-red-500" />;
    if (ext === 'docx' || ext === 'doc') return <FileArchive className="h-3.5 w-3.5 text-blue-500" />;
    return <FileInput className="h-3.5 w-3.5 text-slate-500" />;
  }, [fileName]);

  return (
    <div
      className={cn(
        'p-4 rounded-xl bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 transition-all duration-300 hover:shadow-md group animate-source-card',
      )}
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <div className="flex items-start gap-3 mb-4">
        <div className="flex h-6 w-6 items-center justify-center shrink-0 rounded bg-blue-500 text-white font-bold text-[10px]">
          {index}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-0.5">
            {fileIcon}
            <h3 className="text-xs font-semibold text-slate-900 dark:text-white truncate">
              {fileName}
            </h3>
          </div>
          <p className="text-[10px] text-slate-500 font-medium">
             Page {source.metadata?.page || 'N/A'} • {source.domain || 'Uncategorized'}
          </p>
        </div>
      </div>

      <div className="space-y-3">
        <p className={cn(
          "text-xs text-slate-700 dark:text-slate-300 leading-relaxed",
          !expanded && "line-clamp-3"
        )}>
          "{source.excerpt || source.content || 'No content snippet available.'}"
        </p>

        {source.excerpt && source.excerpt.length > 120 && (
          <button 
            onClick={() => setExpanded(!expanded)}
            className="text-[10px] font-bold text-blue-500 hover:text-blue-600 uppercase tracking-wider"
          >
            {expanded ? 'Show Less' : 'View Full Snippet'}
          </button>
        )}

        <div className="pt-3 border-t border-slate-100 dark:border-slate-700/50">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Confidence</span>
            <span className="text-[10px] font-bold text-blue-500 italic">{relevancePercentage}%</span>
          </div>
          <div className="w-full h-1 bg-slate-100 dark:bg-slate-700/50 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-1000 ease-out"
              style={{ width: `${relevancePercentage}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
