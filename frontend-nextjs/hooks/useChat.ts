/**
 * Enhanced useChat hook with proper error handling and state management
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Message } from '@/lib/types';
import { sendQuery, ApiError } from '@/lib/api-client';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session ID on mount
  useEffect(() => {
    setSessionId(uuidv4());
  }, []);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const sendMessage = useCallback(
    async (question: string) => {
      if (!question.trim() || !sessionId) return;

      const userMessageId = uuidv4();
      const userMessage: Message = {
        id: userMessageId,
        role: 'user',
        content: question,
        timestamp: new Date(),
      };

      // Optimistically add user message
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      // Add typing indicator
      const typingMessageId = uuidv4();
      setMessages((prev) => [
        ...prev,
        {
          id: typingMessageId,
          role: 'assistant',
          content: 'Researching your question...',
          timestamp: new Date(),
        },
      ]);

      try {
        const response = await sendQuery(question, sessionId);

        if (response.success === false && response.error) {
          throw new ApiError(
            null,
            response.error_type || 'query_error',
            response.error
          );
        }

        const assistantMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
          timestamp: new Date(),
        };

        // Replace typing indicator with actual response
        setMessages((prev) => {
          const filtered = prev.filter((msg) => msg.id !== typingMessageId);
          return [...filtered, assistantMessage];
        });
      } catch (err) {
        const errorMessage =
          err instanceof ApiError ? err.message : 'An error occurred';
        const isSafetyBlock =
          err instanceof ApiError && err.errorType === 'safety_block';

        const errorMsg: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: isSafetyBlock
            ? `🚫 ${errorMessage}`
            : `⚠️ ${errorMessage}`,
          timestamp: new Date(),
          error: errorMessage,
          isSafetyBlock,
        };

        setMessages((prev) => {
          const filtered = prev.filter((msg) => msg.id !== typingMessageId);
          return [...filtered, errorMsg];
        });
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    setIsLoading(false);
    setSessionId(uuidv4());
  }, []);

  return {
    messages,
    isLoading,
    error,
    sessionId,
    sendMessage,
    clearChat,
    messagesEndRef,
  };
}
