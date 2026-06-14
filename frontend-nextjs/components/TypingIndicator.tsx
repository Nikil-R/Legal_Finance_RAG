'use client';

export function TypingIndicator() {
  return (
    <div className="flex gap-1 items-center px-4 py-3 bg-card border border-border rounded-2xl rounded-tl-none shadow-sm w-fit animate-message">
      <div className="typing-dot" style={{ animationDelay: '0ms' }} />
      <div className="typing-dot" style={{ animationDelay: '200ms' }} />
      <div className="typing-dot" style={{ animationDelay: '400ms' }} />
    </div>
  );
}
