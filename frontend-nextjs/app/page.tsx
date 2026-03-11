'use client';

import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { SourcesPanel } from '@/components/SourcesPanel';
import { WelcomeScreen } from '@/components/WelcomeScreen';
import { TypingIndicator } from '@/components/TypingIndicator';
import { ScrollToBottom } from '@/components/ScrollToBottom';
import { useChat } from '@/hooks/useChat';
import { useHealth } from '@/hooks/useHealth';
import { cn } from '@/lib/utils';
import { BookOpen } from 'lucide-react';

export default function Home() {
  const { messages, isLoading, sendMessage, clearChat, messagesEndRef } = useChat();
  const { isHealthy } = useHealth();
  
  // UI State
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  // Resize listener for responsive behavior
  useEffect(() => {
    const checkRes = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (mobile) setSourcesOpen(false);
      else setSourcesOpen(true);
    };
    checkRes();
    window.addEventListener('resize', checkRes);
    return () => window.removeEventListener('resize', checkRes);
  }, []);

  const handleStarterQuestion = useCallback((q: string) => {
    sendMessage(q);
  }, [sendMessage]);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const toggleSources = () => setSourcesOpen(!sourcesOpen);

  // Check if we have sources in the latest message
  const hasSources = useMemo(() => {
    const lastAI = [...messages].reverse().find(m => m.role === 'assistant');
    return (lastAI?.sources?.length ?? 0) > 0;
  }, [messages]);

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-50 dark:bg-slate-950">
      <Header 
        onNewChat={clearChat} 
        onMenuClick={toggleSidebar} 
      />

      <div className="flex flex-1 overflow-hidden relative">
        {/* Sidebar overlay for mobile */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[45] lg:hidden animate-in fade-in"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar */}
        <div className={cn(
          "fixed inset-y-0 left-0 z-50 w-72 transform lg:relative lg:translate-x-0 transition-transform duration-300 ease-out",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}>
          <Sidebar onClose={() => setSidebarOpen(false)} />
        </div>

        {/* Main Chat Container */}
        <main className="flex-1 flex flex-col min-w-0 bg-white dark:bg-slate-950 relative">
          <div 
            ref={chatScrollRef}
            className="flex-1 overflow-y-auto scrollbar-thin"
          >
            {messages.length === 0 ? (
              <WelcomeScreen onStarterClick={handleStarterQuestion} />
            ) : (
              <div className="max-w-4xl mx-auto w-full p-4 sm:p-8 space-y-8 pb-32">
                {messages.map((msg) => (
                  <ChatMessage 
                    key={msg.id} 
                    message={msg} 
                    onCitationClick={() => !isMobile && setSourcesOpen(true)}
                  />
                ))}
                
                {isLoading && (
                  <div className="flex gap-4">
                     <div className="h-9 w-9" /> {/* Spacer for avatar */}
                     <TypingIndicator />
                  </div>
                )}
                
                <div ref={messagesEndRef} className="h-4" />
              </div>
            )}
          </div>

          {/* Sources Trigger (Tablet/Mobile) */}
          {hasSources && !sourcesOpen && (
            <div className="absolute top-4 right-4 z-20">
              <button 
                onClick={toggleSources}
                className="flex items-center gap-2 px-3 py-1.5 bg-blue-500 text-white rounded-full text-[10px] font-bold uppercase shadow-lg shadow-blue-500/20 hover:scale-105 transition-all"
              >
                <BookOpen className="h-3 w-3" />
                {isMobile ? 'View Sources' : 'Open Citations'}
              </button>
            </div>
          )}

          {/* Floating Scroll Down */}
          <ScrollToBottom 
            messagesEndRef={messagesEndRef as any}
            messageCount={messages.length}
            previousMessageCount={0}
          />

          {/* Input Area */}
          <div className="mt-auto">
            <ChatInput 
              onSend={sendMessage} 
              isLoading={isLoading} 
              isBackendHealthy={isHealthy}
              onUploadClick={toggleSidebar}
            />
          </div>
        </main>

        {/* Sources Panel */}
        <div className={cn(
          "fixed inset-y-0 right-0 z-50 lg:relative lg:translate-x-0 transition-transform duration-300 ease-in-out",
          sourcesOpen ? "translate-x-0" : "translate-x-full",
          isMobile && "w-full" // Bottom sheet alternative would be better but let's stick to slide-over for now
        )}>
          <SourcesPanel 
            messages={messages} 
            isOpen={sourcesOpen}
            onClose={() => setSourcesOpen(false)} 
          />
        </div>
      </div>
    </div>
  );
}
