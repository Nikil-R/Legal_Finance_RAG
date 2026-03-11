'use client';

import { ArrowDown } from 'lucide-react';
import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface ScrollToBottomProps {
  messagesEndRef: React.RefObject<HTMLDivElement>;
  messageCount?: number;
  previousMessageCount?: number;
}

export function ScrollToBottom({
  messagesEndRef,
  messageCount = 0,
  previousMessageCount = 0,
}: ScrollToBottomProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [newMessageBadge, setNewMessageBadge] = useState(0);
  const [scrollContainer, setScrollContainer] = useState<HTMLElement | null>(null);

  // Find the scroll container (the parent overflow-y-auto element)
  useEffect(() => {
    const container = messagesEndRef.current?.closest('.overflow-y-auto');
    setScrollContainer(container as HTMLElement);
  }, [messagesEndRef]);

  // Monitor scroll position
  useEffect(() => {
    const handleScroll = () => {
      if (!scrollContainer) return;

      const { scrollHeight, scrollTop, clientHeight } = scrollContainer;
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

      // Show button if scrolled up more than 200px
      setIsVisible(distanceFromBottom > 200);
    };

    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', handleScroll);
      return () => scrollContainer.removeEventListener('scroll', handleScroll);
    }
  }, [scrollContainer]);

  // Track new messages
  useEffect(() => {
    if (messageCount > previousMessageCount && isVisible) {
      const newCount = messageCount - previousMessageCount;
      setNewMessageBadge(newCount);
    }
  }, [messageCount, previousMessageCount, isVisible]);

  const handleClick = () => {
    if (scrollContainer && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
      setNewMessageBadge(0);
    }
  };

  if (!isVisible) return null;

  return (
    <button
      onClick={handleClick}
      className={cn(
        'fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50',
        'flex items-center gap-2 px-4 py-3 rounded-full',
        'bg-blue-600 hover:bg-blue-700 text-white shadow-lg',
        'transition-all duration-200 ease-out',
        'animate-fade-in-up',
        'dark:bg-blue-600 dark:hover:bg-blue-700'
      )}
      title="Scroll to bottom"
      aria-label="Scroll to latest messages"
    >
      <ArrowDown className="h-4 w-4" />
      <span className="text-sm font-medium">New message</span>
      {newMessageBadge > 0 && (
        <span className="ml-1 flex items-center justify-center w-5 h-5 rounded-full bg-red-500 text-white text-xs font-semibold">
          {newMessageBadge > 99 ? '99+' : newMessageBadge}
        </span>
      )}
    </button>
  );
}
