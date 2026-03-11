'use client';

import { useState, useCallback } from 'react';
import { Settings, X } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface SettingsDialogProps {
  onSettingsChange?: (settings: UserSettings) => void;
}

export interface UserSettings {
  darkMode: boolean;
  showSources: boolean;
  autoScroll: boolean;
  fontSize: 'small' | 'medium' | 'large';
  markdown: boolean;
  notifications: boolean;
}

const DEFAULT_SETTINGS: UserSettings = {
  darkMode: true,
  showSources: true,
  autoScroll: true,
  fontSize: 'medium',
  markdown: true,
  notifications: true,
};

export function SettingsDialog({ onSettingsChange }: SettingsDialogProps) {
  const [open, setOpen] = useState(false);
  const [settings, setSettings] = useState<UserSettings>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('legalfinance-settings');
      return saved ? JSON.parse(saved) : DEFAULT_SETTINGS;
    }
    return DEFAULT_SETTINGS;
  });

  const updateSetting = useCallback(
    <K extends keyof UserSettings>(key: K, value: UserSettings[K]) => {
      const newSettings = { ...settings, [key]: value };
      setSettings(newSettings);
      
      // Save to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('legalfinance-settings', JSON.stringify(newSettings));
      }
      
      onSettingsChange?.(newSettings);
    },
    [settings, onSettingsChange]
  );

  const resetSettings = useCallback(() => {
    setSettings(DEFAULT_SETTINGS);
    if (typeof window !== 'undefined') {
      localStorage.setItem('legalfinance-settings', JSON.stringify(DEFAULT_SETTINGS));
    }
    onSettingsChange?.(DEFAULT_SETTINGS);
  }, [onSettingsChange]);

  if (!open) {
    return (
      <Button 
        variant="ghost" 
        size="icon"
        className="h-9 w-9"
        onClick={() => setOpen(true)}
        title="Settings"
      >
        <Settings className="h-4 w-4" />
      </Button>
    );
  }

  return (
    <>
      {/* Modal Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={() => setOpen(false)}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white dark:bg-slate-900 rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-200 dark:border-slate-700 p-6 sticky top-0 bg-white dark:bg-slate-900">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Settings
              </h2>
              <p className="text-sm text-gray-600 dark:text-slate-400">
                Customize your LegalFinanceAI experience
              </p>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="space-y-6 p-6">
            {/* Display Settings */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                Display
              </h3>

              {/* Dark Mode */}
              <div className="flex items-center justify-between">
                <label htmlFor="darkMode" className="text-sm font-medium text-gray-700 dark:text-slate-300">
                  Dark Mode
                </label>
                <input
                  id="darkMode"
                  type="checkbox"
                  checked={settings.darkMode}
                  onChange={(e) =>
                    updateSetting('darkMode', e.target.checked)
                  }
                  className="h-4 w-4 rounded border-gray-300 text-blue-600"
                />
              </div>

              {/* Font Size */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-slate-300">Font Size</label>
                <div className="flex gap-2">
                  {(['small', 'medium', 'large'] as const).map((size) => (
                    <button
                      key={size}
                      onClick={() => updateSetting('fontSize', size)}
                      className={`flex-1 px-3 py-2 text-sm rounded-md font-medium transition-colors capitalize ${
                        settings.fontSize === size
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-200 dark:bg-slate-700 text-gray-900 dark:text-slate-300 hover:bg-gray-300 dark:hover:bg-slate-600'
                      }`}
                    >
                      {size}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Behavior Settings */}
            <div className="space-y-4 border-t border-gray-200 dark:border-slate-700 pt-4">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                Behavior
              </h3>

              {/* Auto Scroll */}
              <div className="flex items-center justify-between">
                <label htmlFor="autoScroll" className="text-sm font-medium text-gray-700 dark:text-slate-300">
                  Auto-scroll to latest message
                </label>
                <input
                  id="autoScroll"
                  type="checkbox"
                  checked={settings.autoScroll}
                  onChange={(e) =>
                    updateSetting('autoScroll', e.target.checked)
                  }
                  className="h-4 w-4 rounded border-gray-300 text-blue-600"
                />
              </div>

              {/* Show Sources */}
              <div className="flex items-center justify-between">
                <label htmlFor="showSources" className="text-sm font-medium text-gray-700 dark:text-slate-300">
                  Show sources panel
                </label>
                <input
                  id="showSources"
                  type="checkbox"
                  checked={settings.showSources}
                  onChange={(e) =>
                    updateSetting('showSources', e.target.checked)
                  }
                  className="h-4 w-4 rounded border-gray-300 text-blue-600"
                />
              </div>

              {/* Markdown */}
              <div className="flex items-center justify-between">
                <label htmlFor="markdown" className="text-sm font-medium text-gray-700 dark:text-slate-300">
                  Render Markdown
                </label>
                <input
                  id="markdown"
                  type="checkbox"
                  checked={settings.markdown}
                  onChange={(e) =>
                    updateSetting('markdown', e.target.checked)
                  }
                  className="h-4 w-4 rounded border-gray-300 text-blue-600"
                />
              </div>
            </div>

            {/* Notification Settings */}
            <div className="space-y-4 border-t border-gray-200 dark:border-slate-700 pt-4">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                Notifications
              </h3>

              {/* Enable Notifications */}
              <div className="flex items-center justify-between">
                <label htmlFor="notifications" className="text-sm font-medium text-gray-700 dark:text-slate-300">
                  Enable notifications
                </label>
                <input
                  id="notifications"
                  type="checkbox"
                  checked={settings.notifications}
                  onChange={(e) =>
                    updateSetting('notifications', e.target.checked)
                  }
                  className="h-4 w-4 rounded border-gray-300 text-blue-600"
                />
              </div>
            </div>

            {/* Reset Button */}
            <div className="border-t border-gray-200 dark:border-slate-700 pt-4">
              <Button
                variant="outline"
                onClick={resetSettings}
                className="w-full"
              >
                Reset to Defaults
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
