'use client';

import { Trash2, MessageSquare } from 'lucide-react';

export interface ConversationItem {
  id: string;
  title: string;
  timestamp: Date;
  messageCount: number;
}

interface ConversationHistoryProps {
  conversations: ConversationItem[];
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
}

export function ConversationHistory({
  conversations,
  onSelectConversation,
  onDeleteConversation,
}: ConversationHistoryProps) {
  if (conversations.length === 0) {
    return (
      <div>
        <h3 className="text-sm font-semibold text-slate-100 mb-3">
          Conversation History
        </h3>
        <p className="text-xs text-slate-500">
          Your conversations will appear here. Start a new chat to begin.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-100 mb-3">
        Conversation History
      </h3>
      <div className="space-y-2">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className="group flex items-start gap-2 p-2 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
            onClick={() => onSelectConversation(conv.id)}
          >
            <MessageSquare className="h-4 w-4 text-slate-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-slate-200 truncate">
                {conv.title}
              </p>
              <p className="text-xs text-slate-500">
                {conv.messageCount} message{conv.messageCount !== 1 ? 's' : ''}
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDeleteConversation(conv.id);
              }}
              className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 rounded transition-all"
              title="Delete conversation"
            >
              <Trash2 className="h-3 w-3 text-red-400" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
