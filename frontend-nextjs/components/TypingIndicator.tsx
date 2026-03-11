'use client';

export function TypingIndicator() {
  return (
    <div className="flex gap-1 items-center px-4 py-3 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl rounded-tl-none shadow-sm w-fit animate-message">
      <div className="typing-dot" style={{ animationDelay: '0ms' }} />
      <div className="typing-dot" style={{ animationDelay: '200ms' }} />
      <div className="typing-dot" style={{ animationDelay: '400ms' }} />
    </div>
  );
}
