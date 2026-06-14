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
      "w-80 border-l border-primary/20 bg-[#0A0A0A]/80 backdrop-blur-md flex flex-col h-full shadow-lg sticky top-0 right-0 z-30 transition-all duration-300",
      "lg:flex hidden" // Responsive hide handled by parent layout mostly, but explicit here too
    )}>
      {/* Header */}
      <div className="border-b border-border p-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/20">
            <FileText className="h-4 w-4 text-primary" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-foreground">
              Citations
            </h2>
            <p className="text-xs text-muted">
              {sources.length} document{sources.length === 1 ? '' : 's'} linked
            </p>
          </div>
        </div>
        <button 
          onClick={onClose}
          className="p-2 hover:bg-background rounded-lg transition-colors"
          aria-label="Close sources panel"
        >
          <X className="h-4 w-4 text-muted" />
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
        'p-4 rounded-xl bg-background border border-border transition-all duration-300 hover:border-primary/50 hover:shadow-md hover:shadow-primary/5 group animate-source-card',
      )}
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <div className="flex items-start gap-3 mb-4">
        <div className="flex h-6 w-6 items-center justify-center shrink-0 rounded bg-primary text-[#0A0A0A] font-bold text-[10px]">
          {index}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-0.5">
            {fileIcon}
            <h3 className="text-xs font-semibold text-foreground truncate">
              {fileName}
            </h3>
          </div>
          <p className="text-[10px] text-muted font-medium">
             Page {source.metadata?.page || 'N/A'} • {source.domain || 'Uncategorized'}
          </p>
        </div>
      </div>

      <div className="space-y-3">
        <p className={cn(
          "text-xs text-muted leading-relaxed",
          !expanded && "line-clamp-3"
        )}>
          "{source.excerpt || source.content || 'No content snippet available.'}"
        </p>

        {source.excerpt && source.excerpt.length > 120 && (
          <button 
            onClick={() => setExpanded(!expanded)}
            className="text-[10px] font-bold text-primary hover:text-primary-dark uppercase tracking-wider"
          >
            {expanded ? 'Show Less' : 'View Full Snippet'}
          </button>
        )}

        <div className="pt-3 border-t border-border">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] font-bold text-muted uppercase tracking-tighter">Confidence</span>
            <span className="text-[10px] font-bold text-primary italic">{relevancePercentage}%</span>
          </div>
          <div className="w-full h-1 bg-background rounded-full overflow-hidden border border-border">
            <div
              className="h-full bg-gradient-to-r from-primary to-primary-dark transition-all duration-1000 ease-out"
              style={{ width: `${relevancePercentage}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
