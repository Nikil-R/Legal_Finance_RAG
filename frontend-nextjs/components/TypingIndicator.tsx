'use client';

export function TypingIndicator() {
  return (
    <div className="flex gap-1 items-center">
      <div className="h-2 w-2 bg-blue-600 dark:bg-blue-400 rounded-full animate-bounce" />
      <div className="h-2 w-2 bg-blue-600 dark:bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
      <div className="h-2 w-2 bg-blue-600 dark:bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
      <span className="text-sm text-gray-600 dark:text-slate-400 ml-2">AI is thinking...</span>
    </div>
  );
}
