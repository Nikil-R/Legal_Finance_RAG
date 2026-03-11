'use client';

import React from 'react';
import ReactMarkdown, { Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/utils';

interface MarkdownRendererProps {
  content: string;
  onCitationClick?: (citationNumber: number) => void;
}

export function MarkdownRenderer({ content, onCitationClick }: MarkdownRendererProps) {
  // Custom components for react-markdown
  const components: Components = {
    // Headings
    h1: ({ ...props }) => <h1 className="text-[18px] font-semibold mt-6 mb-3 text-slate-900 dark:text-slate-100" {...props} />,
    h2: ({ ...props }) => <h2 className="text-[18px] font-semibold mt-5 mb-2 text-slate-900 dark:text-slate-100" {...props} />,
    h3: ({ ...props }) => <h3 className="text-base font-semibold mt-4 mb-2 text-slate-900 dark:text-slate-100" {...props} />,

    // Paragraphs
    p: ({ children, ...props }) => {
      // Helper to process text and find citations
      const processText = (text: string) => {
        if (typeof text !== 'string') return text;
        
        const parts = text.split(/(\[\d+\])/g);
        return parts.map((part, i) => {
          const match = part.match(/\[(\d+)\]/);
          if (match) {
            const num = parseInt(match[1]);
            return (
              <button
                key={i}
                onClick={() => onCitationClick?.(num)}
                className="citation-badge"
              >
                {num}
              </button>
            );
          }
          return part;
        });
      };

      // Deeply traverse children to replace citation patterns in text strings
      const recursiveProcess = (node: React.ReactNode): React.ReactNode => {
        if (typeof node === 'string') {
          return processText(node);
        }
        if (React.isValidElement(node) && node.props.children) {
          return React.cloneElement(node as React.ReactElement, {
            ...node.props,
            children: React.Children.map(node.props.children, recursiveProcess)
          });
        }
        return node;
      };

      const processedChildren = React.Children.map(children, recursiveProcess);
      
      // Check for disclaimer
      const contentStr = React.Children.toArray(children).join('').toLowerCase();
      const isDisclaimer = contentStr.includes('disclaimer:');

      return (
        <p 
          className={cn(
            "mb-3 leading-relaxed",
            isDisclaimer ? "text-slate-400 text-xs mt-4 italic" : "text-slate-800 dark:text-slate-200"
          )} 
          {...props}
        >
          {processedChildren}
        </p>
      );
    },

    // Lists
    ul: ({ ...props }) => <ul className="list-disc list-outside mb-4 ml-5 space-y-1.5" {...props} />,
    ol: ({ ...props }) => <ol className="list-decimal list-outside mb-4 ml-5 space-y-1.5" {...props} />,
    li: ({ ...props }) => <li className="pl-1 text-slate-800 dark:text-slate-200" {...props} />,

    // Bold
    strong: ({ ...props }) => <strong className="font-bold text-slate-900 dark:text-white" {...props} />,

    // Tables
    table: ({ ...props }) => (
      <div className="overflow-x-auto my-4 rounded-lg border border-slate-200 dark:border-slate-800">
        <table className="min-w-full border-collapse" {...props} />
      </div>
    ),
    th: ({ ...props }) => <th className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-800 px-4 py-2 text-left text-sm font-semibold" {...props} />,
    td: ({ ...props }) => <td className="border-b border-slate-200 dark:border-slate-800 px-4 py-2 text-sm text-slate-800 dark:text-slate-200" {...props} />,
    tr: ({ ...props }) => <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-900/20 even:bg-slate-50/30 dark:even:bg-slate-900/10" {...props} />,

    // Code
    code: ({ node, inline, ...props }: any) => (
      <code
        className={cn(
          "font-mono rounded bg-slate-100 dark:bg-slate-900 px-1 py-0.5 text-sm",
          inline ? "inline text-blue-600 dark:text-blue-400" : "block p-4 my-2 overflow-x-auto text-slate-800 dark:text-slate-200"
        )}
        {...props}
      />
    ),

    // Horizontal Rule
    hr: ({ ...props }) => <hr className="my-6 border-slate-200 dark:border-slate-800" {...props} />,
  };

  return (
    <div className="prose prose-slate dark:prose-invert max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={components}
      >
        {content}
      </ReactMarkdown>

      <style jsx global>{`
        .citation-badge {
          background-color: #3b82f6;
          color: white !important;
          border-radius: 4px;
          padding: 1px 6px;
          margin: 0 4px;
          font-size: 11px;
          font-weight: 700;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          vertical-align: middle;
          border: none;
          line-height: normal;
          transform: translateY(-1px);
        }
        .citation-badge:hover {
          background-color: #2563eb;
        }
      `}</style>
    </div>
  );
}
