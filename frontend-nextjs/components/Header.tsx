'use client';

import { useEffect, useState } from 'react';
import { useHealth } from '@/hooks/useHealth';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { AlertCircle, Zap, Settings, Menu, PlusCircle, RefreshCw, Download } from 'lucide-react';
import { SettingsDialog } from './SettingsDialog';

interface Props {
  onNewChat?: () => void;
  onMenuClick?: () => void;
  onExport?: () => void;
  hasMessages?: boolean;
}

export function Header({ onNewChat, onMenuClick, onExport, hasMessages }: Props) {
  const { isHealthy, healthStatus, lastChecked, refresh } = useHealth();
  const [mounted, setMounted] = useState(false);
  const [showStatus, setShowStatus] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <header className="glass-header h-16 sticky top-0 z-40 w-full">
        <div className="max-w-[100vw] px-4 h-full flex items-center justify-between">
           <Zap className="h-6 w-6 text-primary animate-pulse" />
        </div>
      </header>
    );
  }

  const healthBadgeColor = isHealthy
    ? 'bg-green-500/10 text-green-400 border border-green-500/20'
    : 'bg-red-500/10 text-red-400 border border-red-500/20';
  
  const healthBadgeIcon = isHealthy ? (
    <div className="h-2 w-2 rounded-full bg-green-400 animate-soft-pulse" />
  ) : (
    <AlertCircle className="h-3.5 w-3.5" />
  );

  return (
    <header className="glass-header h-16 sticky top-0 z-40 w-full px-4 sm:px-6">
      <div className="h-full flex items-center justify-between">
        {/* Left: Mobile Menu + Logo */}
        <div className="flex items-center gap-3">
          <button 
            onClick={onMenuClick}
            className="p-2 hover:bg-card rounded-lg"
            aria-label="Open sidebar"
          >
            <Menu className="h-5 w-5 text-muted" />
          </button>
          
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-dark shadow-primary/20 shadow-lg animate-float border border-primary/30">
              <Zap className="h-5 w-5 text-[#0A0A0A]" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold tracking-tight brand-gradient">
                LegalFinanceAI
              </h1>
              <p className="text-[10px] uppercase tracking-widest font-bold text-muted">v1.0 • RAG ENGINE</p>
            </div>
          </div>
        </div>

        {/* Right: Status + Actions */}
        <div className="flex items-center gap-2 sm:gap-4">
          {/* Health Status Button */}
          <div className="relative">
            <button
              onClick={() => setShowStatus(!showStatus)}
              className={cn(
                'flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-bold uppercase tracking-wider transition-all',
                healthBadgeColor
              )}
            >
              {healthBadgeIcon}
              <span className="hidden md:inline">{isHealthy ? 'System Online' : 'System Offline'}</span>
              <span className="md:hidden">Status</span>
            </button>

            {showStatus && (
              <div className="absolute right-0 mt-3 w-72 bg-card border border-border rounded-2xl shadow-2xl p-4 z-50 animate-message">
                <div className="flex items-center justify-between mb-4 border-b border-border pb-2">
                  <span className="text-xs font-bold text-foreground uppercase tracking-tight">Backend Pulse</span>
                  <button 
                    onClick={() => { refresh(); setShowStatus(false); }}
                    className="p-1.5 hover:bg-background rounded-lg"
                  >
                    <RefreshCw className="h-3 w-3 text-muted" />
                  </button>
                </div>
                
                {healthStatus?.checks && (
                  <div className="space-y-3">
                    {Object.entries(healthStatus.checks).map(([service, info]: any) => (
                      <div key={service} className="flex justify-between items-center py-1 border-b border-border last:border-0">
                        <span className="text-[11px] font-medium text-muted capitalize">{service}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-[11px] font-mono text-muted">{info.latency_ms.toFixed(1)}ms</span>
                          <div className={cn(
                            'h-1.5 w-1.5 rounded-full',
                            info.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                          )} />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="mt-4 pt-3 border-t border-border text-[10px] text-muted text-center italic">
                  Last verified: {lastChecked ? lastChecked.toLocaleTimeString() : 'Pending'}
                </div>
              </div>
            )}
          </div>

          <div className="h-4 w-px bg-border hidden sm:block mx-1" />

          {/* Settings Trigger */}
          <SettingsDialog />

          {/* Export Chat Button */}
          {hasMessages && (
            <button
              onClick={onExport}
              className="hidden md:flex items-center gap-2 px-3 py-2 border border-border hover:border-primary/50 hover:bg-primary/5 rounded-xl text-xs font-bold transition-all"
              title="Export Conversation"
            >
              <Download className="h-3.5 w-3.5" />
              <span className="hidden lg:inline">Export</span>
            </button>
          )}

          {/* New Chat Button */}
          <button
            onClick={onNewChat}
            className="hidden md:flex items-center gap-2 px-4 py-2 bg-primary text-[#0A0A0A] rounded-xl text-xs font-bold transition-all hover:brightness-110 active:scale-95 shadow-lg shadow-primary/20"
          >
            <PlusCircle className="h-3.5 w-3.5" />
            New Session
          </button>
          
          <button
            onClick={onNewChat}
            className="md:hidden p-2 hover:bg-card rounded-lg text-muted"
            aria-label="New chat"
          >
            <PlusCircle className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
