'use client';

import { useEffect, useState } from 'react';
import { useHealth } from '@/hooks/useHealth';
import { Button } from '@/components/ui/Button';
import { AlertCircle, Check, Zap } from 'lucide-react';

interface Props {
  onNewChat?: () => void;
}

export function Header({ onNewChat }: Props) {
  const { isHealthy, healthStatus, lastChecked, refresh } = useHealth();
  const [mounted, setMounted] = useState(false);
  const [showStatus, setShowStatus] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleNewChat = () => {
    onNewChat?.();
  };

  if (!mounted) {
    return (
      <header className="border-b bg-white/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="h-6 w-6 text-blue-600" />
              <h1 className="text-lg font-bold text-gray-900">
                LegalFinanceAI
              </h1>
            </div>
            <div className="h-8 w-12 bg-gray-200 rounded animate-pulse" />
          </div>
        </div>
      </header>
    );
  }

  const healthBadgeColor = isHealthy
    ? 'bg-green-100 text-green-800'
    : 'bg-red-100 text-red-800';
  const healthBadgeIcon = isHealthy ? (
    <Check className="h-3.5 w-3.5" />
  ) : (
    <AlertCircle className="h-3.5 w-3.5" />
  );

  const formatLastChecked = (date: Date | null) => {
    if (!date) return 'Never';
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);

    if (diffSecs < 60) return 'Just now';
    if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}m ago`;
    if (diffSecs < 86400) return `${Math.floor(diffSecs / 3600)}h ago`;
    return `${Math.floor(diffSecs / 86400)}d ago`;
  };

  const getServiceColor = (status: string) => {
    switch (status) {
      case 'operational':
        return 'text-green-600';
      case 'degraded':
        return 'text-yellow-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getServiceDot = (status: string) => {
    switch (status) {
      case 'operational':
        return 'bg-green-600';
      case 'degraded':
        return 'bg-yellow-600';
      case 'down':
        return 'bg-red-600';
      default:
        return 'bg-gray-600';
    }
  };

  return (
    <header className="border-b border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm sticky top-0 z-40">
      <div className="mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo Section */}
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-blue-700">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold text-gray-900">LegalFinanceAI</h1>
              <p className="text-xs text-gray-500">RAG Assistant</p>
            </div>
            <div className="sm:hidden">
              <h1 className="text-base font-bold text-gray-900">LegalFinance</h1>
            </div>
          </div>

          {/* Right Section - Health Badge + New Chat */}
          <div className="flex items-center gap-2 sm:gap-4 relative">
            {/* Health Badge */}
            <button
              onClick={() => setShowStatus(!showStatus)}
              className={`gap-2 inline-flex items-center px-3 py-1.5 rounded-md text-xs font-medium ${healthBadgeColor} hover:opacity-85 transition-opacity cursor-pointer border-0`}
            >
              {healthBadgeIcon}
              <span className="hidden sm:inline">
                {isHealthy ? 'All Systems' : 'Issue Detected'}
              </span>
              <span className="sm:hidden">
                {isHealthy ? 'OK' : 'Error'}
              </span>
            </button>

            {/* Health Status Dropdown */}
            {showStatus && (
              <div className="absolute right-0 mt-2 top-full w-80 bg-white border border-gray-200 rounded-lg shadow-lg p-4 space-y-3 z-50">
                {/* Header */}
                <div className="flex items-center justify-between border-b pb-2">
                  <span className="font-semibold text-gray-900 text-sm">
                    System Status
                  </span>
                  <button
                    onClick={() => {
                      refresh();
                      setShowStatus(false);
                    }}
                    className="text-xs px-2 py-1 rounded hover:bg-gray-100 text-gray-700"
                  >
                    Refresh
                  </button>
                </div>

                {/* Last Checked */}
                <div className="text-xs text-gray-600">
                  Last checked: {formatLastChecked(lastChecked)}
                </div>

                {/* Service Status */}
                {healthStatus?.checks && (
                  <div className="space-y-2">
                    {Object.entries(healthStatus.checks).map(
                      ([serviceName, serviceStatus]: [string, any]) => {
                        const displayName = serviceName
                          .split('_')
                          .map(
                            (word) =>
                              word.charAt(0).toUpperCase() + word.slice(1)
                          )
                          .join(' ');
                        const status = serviceStatus?.status || 'unknown';

                        return (
                          <div key={serviceName} className="flex items-start gap-2">
                            <div
                              className={`mt-1 h-2 w-2 rounded-full flex-shrink-0 ${getServiceDot(status)}`}
                            />
                            <div className="flex-1 min-w-0">
                              <div className={`text-sm font-medium ${getServiceColor(status)}`}>
                                {displayName}
                              </div>
                              {serviceStatus?.details && (
                                <div className="text-xs text-gray-600 truncate">
                                  {serviceStatus.details}
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      }
                    )}
                  </div>
                )}

                {/* Overall Status */}
                <div className="border-t pt-2 text-xs text-gray-600">
                  Overall:{' '}
                  <span className={isHealthy ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
                    {isHealthy ? 'Operational' : 'Degraded'}
                  </span>
                </div>
              </div>
            )}

            {/* New Chat Button */}
            {onNewChat && (
              <Button
                onClick={handleNewChat}
                size="sm"
                className="gap-2 bg-blue-600 hover:bg-blue-700"
              >
                New Chat
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Click outside to close */}
      {showStatus && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowStatus(false)}
        />
      )}
    </header>
  );
}
