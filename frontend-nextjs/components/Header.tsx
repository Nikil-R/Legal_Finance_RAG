'use client';

import { useEffect, useState } from 'react';
import { useHealth } from '@/hooks/useHealth';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { AlertCircle, Zap, Settings, Menu, PlusCircle, RefreshCw } from 'lucide-react';
import { SettingsDialog } from './SettingsDialog';

interface Props {
  onNewChat?: () => void;
  onMenuClick?: () => void;
}

export function Header({ onNewChat, onMenuClick }: Props) {
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
           <Zap className="h-6 w-6 text-blue-500 animate-pulse" />
        </div>
      </header>
    );
  }

  const healthBadgeColor = isHealthy
    ? 'bg-green-100 dark:bg-green-500/10 text-green-800 dark:text-green-300'
    : 'bg-red-100 dark:bg-red-500/10 text-red-800 dark:text-red-300';
  
  const healthBadgeIcon = isHealthy ? (
    <div className="h-2 w-2 rounded-full bg-green-500 animate-soft-pulse" />
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
            className="lg:hidden p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg"
            aria-label="Open sidebar"
          >
            <Menu className="h-5 w-5 text-slate-600 dark:text-slate-400" />
          </button>
          
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 shadow-blue-500/20 shadow-lg animate-float">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold tracking-tight brand-gradient">
                LegalFinanceAI
              </h1>
              <p className="text-[10px] uppercase tracking-widest font-bold text-slate-400 dark:text-slate-500">v1.0 • RAG ENGINE</p>
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
              <div className="absolute right-0 mt-3 w-72 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl p-4 z-50 animate-message">
                <div className="flex items-center justify-between mb-4 border-b border-slate-100 dark:border-slate-800 pb-2">
                  <span className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-tight">Backend Pulse</span>
                  <button 
                    onClick={() => { refresh(); setShowStatus(false); }}
                    className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg"
                  >
                    <RefreshCw className="h-3 w-3 text-slate-400" />
                  </button>
                </div>
                
                {healthStatus?.checks && (
                  <div className="space-y-3">
                    {Object.entries(healthStatus.checks).map(([service, info]: any) => (
                      <div key={service} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className={cn(
                            'h-1.5 w-1.5 rounded-full',
                            info.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                          )} />
                          <span className="text-[11px] font-medium text-slate-600 dark:text-slate-400 capitalize">{service}</span>
                        </div>
                        <span className="text-[11px] font-mono text-slate-400">{info.latency_ms.toFixed(1)}ms</span>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-[10px] text-slate-400 text-center italic">
                  Last verified: {lastChecked ? lastChecked.toLocaleTimeString() : 'Pending'}
                </div>
              </div>
            )}
          </div>

          <div className="h-4 w-px bg-slate-200 dark:bg-slate-800 hidden sm:block mx-1" />

          {/* Settings Trigger */}
          <SettingsDialog />

          {/* New Chat Button */}
          <button
            onClick={onNewChat}
            className="hidden md:flex items-center gap-2 px-4 py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl text-xs font-bold transition-all hover:opacity-90 active:scale-95 shadow-lg shadow-slate-200 dark:shadow-none"
          >
            <PlusCircle className="h-3.5 w-3.5" />
            New Session
          </button>
          
          <button
            onClick={onNewChat}
            className="md:hidden p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-600"
            aria-label="New chat"
          >
            <PlusCircle className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
