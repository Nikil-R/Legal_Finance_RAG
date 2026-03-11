'use client';

interface MessageGroupingProps {
  date: Date;
}

export function MessageGrouping({ date }: MessageGroupingProps) {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const isToday =
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear();

  const isYesterday =
    date.getDate() === yesterday.getDate() &&
    date.getMonth() === yesterday.getMonth() &&
    date.getFullYear() === yesterday.getFullYear();

  let label = '';
  if (isToday) {
    label = 'Today';
  } else if (isYesterday) {
    label = 'Yesterday';
  } else {
    label = date.toLocaleDateString([], {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined,
    });
  }

  return (
    <div className="flex items-center gap-3 my-6">
      <div className="flex-1 h-px bg-linear-to-r from-slate-600 to-slate-600/0" />
      <p className="text-xs font-medium text-slate-500 dark:text-slate-400 px-2">
        ── {label} ──
      </p>
      <div className="flex-1 h-px bg-linear-to-l from-slate-600 to-slate-600/0" />
    </div>
  );
}
