'use client';

import { useState, useCallback } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { SourcesPanel } from '@/components/SourcesPanel';
import { WelcomeScreen } from '@/components/WelcomeScreen';
import { TypingIndicator } from '@/components/TypingIndicator';
import { useChat } from '@/hooks/useChat';
import { useHealth } from '@/hooks/useHealth';

export default function Home() {
  const { messages, isLoading, error, sendMessage, clearChat, messagesEndRef } =
    useChat();
  const { isHealthy } = useHealth();
  const [typingMessage, setTypingMessage] = useState('');

  const handleNewChat = useCallback(() => {
    clearChat();
  }, [clearChat]);

  const handleStarterQuestion = useCallback(
    (question: string) => {
      sendMessage(question);
    },
    [sendMessage]
  );

  const handleSendMessage = useCallback(
    (message: string) => {
      sendMessage(message);
    },
    [sendMessage]
  );

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gray-50 dark:bg-slate-950">
      {/* Sidebar - Document Upload */}
      <Sidebar />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto">
          <div className="h-full flex flex-col">
            {messages.length === 0 && !isLoading ? (
              <WelcomeScreen onStarterClick={handleStarterQuestion} />
            ) : (
              <div className="flex-1 flex flex-col p-6 md:p-8 lg:p-12 max-w-4xl mx-auto w-full space-y-6">
                {/* Messages */}
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}

                {/* Typing Indicator */}
                {isLoading && (
                  <div className="flex gap-4 mb-4 animate-in fade-in slide-in-from-bottom-2">
                    <div className="flex-shrink-0 flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-500/10">
                      <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">
                        AI
                      </span>
                    </div>
                    <div className="flex items-center">
                      <TypingIndicator />
                    </div>
                  </div>
                )}

                {/* Error Display */}
                {error && (
                  <div className="p-4 rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30">
                    <p className="text-sm text-red-800 dark:text-red-300">
                      {error}
                    </p>
                  </div>
                )}

                {/* Ref for auto-scroll */}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <ChatInput
          onSend={handleSendMessage}
          isLoading={isLoading}
          isBackendHealthy={isHealthy}
        />
      </div>

      {/* Sources Panel - Citations & References */}
      {messages.length > 0 && <SourcesPanel messages={messages} />}
    </div>
  );
}
