/**
 * Enhanced useChat hook — supports real-time SSE streaming with fallback
 * to the regular REST endpoint.
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Message } from '@/lib/types';
import { sendQuery, ApiError } from '@/lib/api-client';
import { streamQuery } from '@/lib/stream-client';

const ENABLE_STREAMING = true; // flip to false to use REST fallback

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortStreamRef = useRef<(() => void) | null>(null);

  // ── Persistence ───────────────────────────────────────────────────────────

  useEffect(() => {
    const savedId = localStorage.getItem('chat_session_id');
    const newId = savedId || uuidv4();
    setSessionId(newId);
    if (!savedId) localStorage.setItem('chat_session_id', newId);

    const savedHistory = localStorage.getItem('chat_history');
    if (savedHistory) {
      try {
        const parsed = JSON.parse(savedHistory);
        setMessages(
          parsed.map((m: Message) => ({ ...m, timestamp: new Date(m.timestamp) }))
        );
      } catch (e) {
        console.error('Failed to load history', e);
      }
    }
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chat_history', JSON.stringify(messages));
    }
  }, [messages]);

  // ── Auto-scroll ───────────────────────────────────────────────────────────

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // ── Streaming send ────────────────────────────────────────────────────────

  const sendMessageStreaming = useCallback(
    async (question: string) => {
      if (!question.trim() || !sessionId) return;

      const userMessage: Message = {
        id: uuidv4(),
        role: 'user',
        content: question,
        timestamp: new Date(),
      };

      const assistantId = uuidv4();
      const assistantMessage: Message = {
        id: assistantId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      setIsLoading(true);
      setIsStreaming(true);
      setError(null);

      let accumulatedContent = '';

      const abort = streamQuery(
        question,
        sessionId,
        {
          onStatus: (status) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: status, isStreaming: true }
                  : m
              )
            );
          },

          onToken: (token) => {
            accumulatedContent += token;
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: accumulatedContent, isStreaming: true }
                  : m
              )
            );
          },

          onSources: (sources, metadata, disclaimer) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, sources, metadata, disclaimer }
                  : m
              )
            );
          },

          onDone: (totalMs) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, isStreaming: false }
                  : m
              )
            );
            setIsLoading(false);
            setIsStreaming(false);
            abortStreamRef.current = null;
          },

          onError: (errMsg) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? {
                      ...m,
                      content: `⚠️ ${errMsg}`,
                      error: errMsg,
                      isStreaming: false,
                    }
                  : m
              )
            );
            setError(errMsg);
            setIsLoading(false);
            setIsStreaming(false);
            abortStreamRef.current = null;
          },
        }
      );

      abortStreamRef.current = abort;
    },
    [sessionId]
  );

  // ── REST fallback send ────────────────────────────────────────────────────

  const sendMessageRest = useCallback(
    async (question: string) => {
      if (!question.trim() || !sessionId) return;

      const userMessage: Message = {
        id: uuidv4(),
        role: 'user',
        content: question,
        timestamp: new Date(),
      };

      const typingId = uuidv4();
      setMessages((prev) => [
        ...prev,
        userMessage,
        {
          id: typingId,
          role: 'assistant',
          content: 'Researching your question…',
          timestamp: new Date(),
        },
      ]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await sendQuery(question, sessionId);

        if (response.success === false && response.error) {
          throw new ApiError(null, response.error_type || 'query_error', response.error);
        }

        const assistantMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
          timestamp: new Date(),
        };

        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== typingId);
          return [...filtered, assistantMessage];
        });
      } catch (err) {
        const errorMessage = err instanceof ApiError ? err.message : 'An error occurred';
        const isSafetyBlock = err instanceof ApiError && err.errorType === 'safety_block';

        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== typingId);
          return [
            ...filtered,
            {
              id: uuidv4(),
              role: 'assistant',
              content: isSafetyBlock ? `🚫 ${errorMessage}` : `⚠️ ${errorMessage}`,
              timestamp: new Date(),
              error: errorMessage,
              isSafetyBlock,
            },
          ];
        });
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  // ── Public API ────────────────────────────────────────────────────────────

  const sendMessage = ENABLE_STREAMING ? sendMessageStreaming : sendMessageRest;

  const cancelStream = useCallback(() => {
    abortStreamRef.current?.();
    abortStreamRef.current = null;
    setIsLoading(false);
    setIsStreaming(false);
  }, []);

  const clearChat = useCallback(() => {
    cancelStream();
    setMessages([]);
    setError(null);
    setSessionId(uuidv4());
    localStorage.removeItem('chat_history');
  }, [cancelStream]);

  return {
    messages,
    isLoading,
    isStreaming,
    error,
    sessionId,
    sendMessage,
    cancelStream,
    clearChat,
    messagesEndRef,
  };
}
