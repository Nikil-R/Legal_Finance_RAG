'use client';

import { createContext, useContext, useState, useCallback } from 'react';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Toast {
  id: string;
  title?: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearAll: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: Toast = { ...toast, id };
    
    setToasts((prev) => [...prev, newToast]);

    // Auto-dismiss after duration (default 5 seconds)
    const duration = toast.duration ?? 5000;
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration);
    }

    return id;
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setToasts([]);
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, clearAll }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
}

interface ToastContainerProps {
  toasts: Toast[];
  removeToast: (id: string) => void;
}

function ToastContainer({ toasts, removeToast }: ToastContainerProps) {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2 max-w-md">
      {toasts.map((toast) => (
        <ToastItem
          key={toast.id}
          toast={toast}
          onDismiss={() => removeToast(toast.id)}
        />
      ))}
    </div>
  );
}

interface ToastItemProps {
  toast: Toast;
  onDismiss: () => void;
}

function ToastItem({ toast, onDismiss }: ToastItemProps) {
  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />;
      case 'info':
        return <Info className="h-5 w-5 text-blue-600 dark:text-blue-400" />;
    }
  };

  const getStyles = () => {
    switch (toast.type) {
      case 'success':
        return 'bg-green-50 dark:bg-green-500/10 border-green-200 dark:border-green-500/30';
      case 'error':
        return 'bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/30';
      case 'warning':
        return 'bg-yellow-50 dark:bg-yellow-500/10 border-yellow-200 dark:border-yellow-500/30';
      case 'info':
        return 'bg-blue-50 dark:bg-blue-500/10 border-blue-200 dark:border-blue-500/30';
    }
  };

  const getTextStyles = () => {
    switch (toast.type) {
      case 'success':
        return 'text-green-900 dark:text-green-300';
      case 'error':
        return 'text-red-900 dark:text-red-300';
      case 'warning':
        return 'text-yellow-900 dark:text-yellow-300';
      case 'info':
        return 'text-blue-900 dark:text-blue-300';
    }
  };

  return (
    <div
      className={cn(
        'flex gap-3 rounded-lg border p-4 shadow-lg animate-in slide-in-from-right-4 fade-in',
        getStyles()
      )}
    >
      <div className="flex-shrink-0">{getIcon()}</div>
      <div className="flex-1">
        {toast.title && (
          <p className={cn('font-semibold text-sm', getTextStyles())}>
            {toast.title}
          </p>
        )}
        <p className={cn('text-sm', getTextStyles())}>
          {toast.message}
        </p>
      </div>
      <button
        onClick={onDismiss}
        className={cn('flex-shrink-0 ml-auto opacity-70 hover:opacity-100', {
          'text-green-600 dark:text-green-400': toast.type === 'success',
          'text-red-600 dark:text-red-400': toast.type === 'error',
          'text-yellow-600 dark:text-yellow-400': toast.type === 'warning',
          'text-blue-600 dark:text-blue-400': toast.type === 'info',
        })}
        title="Dismiss"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}
