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
import { UploadModal } from '@/components/UploadModal';

export default function Home() {
  const { messages, isLoading, sendMessage, clearChat, messagesEndRef } = useChat();
  const { isHealthy } = useHealth();
  
  // UI State
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(true);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
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

  const handleExportChat = () => {
    if (messages.length === 0) return;
    
    let markdownContent = `# LegalFinance AI - Chat Export\n*Generated on: ${new Date().toLocaleString()}*\n\n---\n\n`;
    
    messages.forEach((msg) => {
      if (msg.role === 'user') {
        markdownContent += `### **User**\n\n${msg.content}\n\n`;
      } else {
        markdownContent += `### **LegalFinance AI**\n\n${msg.content}\n\n`;
        if (msg.sources && msg.sources.length > 0) {
          markdownContent += `**Sources Used:**\n`;
          msg.sources.forEach((src, idx) => {
            markdownContent += `- [${idx + 1}] **${src.source}** (Relevance: ${Math.round(src.relevance_score * 100)}%)\n`;
          });
          markdownContent += `\n`;
        }
      }
      markdownContent += `---\n\n`;
    });

    const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${new Date().toISOString().slice(0,10)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Check if we have sources in the latest message
  const hasSources = useMemo(() => {
    const lastAI = [...messages].reverse().find(m => m.role === 'assistant');
    return (lastAI?.sources?.length ?? 0) > 0;
  }, [messages]);

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background">
      <Header 
        onNewChat={clearChat} 
        onMenuClick={toggleSidebar} 
        onExport={handleExportChat}
        hasMessages={messages.length > 0}
      />
      <UploadModal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />

      <div className="flex flex-1 overflow-hidden relative">
        {/* Sidebar overlay for mobile */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 bg-[#0A0A0A]/80 backdrop-blur-sm z-[45] lg:hidden animate-in fade-in"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar */}
        <div className={cn(
          "fixed inset-y-0 left-0 z-50 h-full transition-all duration-300 ease-in-out lg:relative",
          sidebarOpen ? "w-72 translate-x-0" : "w-0 -translate-x-full lg:translate-x-0 overflow-hidden"
        )}>
          <div className="w-72 h-full">
            <Sidebar onClose={() => setSidebarOpen(false)} />
          </div>
        </div>

        {/* Main Chat Container */}
        <main className="flex-1 flex flex-col min-w-0 bg-background relative">
          <div 
            ref={chatScrollRef}
            className="flex-1 overflow-y-auto scrollbar-hide"
          >
            {messages.length === 0 ? (
              <WelcomeScreen onStarterClick={handleStarterQuestion} />
            ) : (
              <div className="max-w-3xl mx-auto w-full p-4 sm:p-8 space-y-8 pb-32">
                {messages.map((msg) => (
                  <ChatMessage 
                    key={msg.id} 
                    message={msg} 
                    onCitationClick={() => !isMobile && setSourcesOpen(true)}
                  />
                ))}
                
                {isLoading && (
                  <div className="flex flex-col gap-2">
                    {messages.filter(m => m.role === 'assistant').length === 0 && (
                      <div className="max-w-md ml-12 p-3 bg-card text-primary text-xs rounded-lg border border-primary/20 animate-pulse-soft">
                        ⏰ First query can take 30-60s while the backend wakes up and loads models. 
                        Subsequent queries will be much faster!
                      </div>
                    )}
                    <div className="flex gap-4">
                      <div className="h-9 w-9" /> {/* Spacer for avatar */}
                      <TypingIndicator />
                    </div>
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
                className="flex items-center gap-2 px-3 py-1.5 bg-card text-primary border border-primary/30 rounded-full text-[10px] font-bold uppercase shadow-lg shadow-primary/10 hover:scale-105 transition-all hover:bg-primary/10"
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
              onUploadClick={() => setIsUploadOpen(true)}
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
