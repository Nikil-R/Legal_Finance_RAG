'use client';

import { useState, useCallback } from 'react';
import { Settings, X, Moon, Sun, Monitor, Info, ShieldCheck, Globe, Database, Cog } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

export function SettingsDialog() {
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'general' | 'advanced' | 'about'>('general');
  const [darkMode, setDarkMode] = useState(true);
  const [apiUrl, setApiUrl] = useState(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

  const toggleTheme = () => {
    const next = !darkMode;
    setDarkMode(next);
    if (next) document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors text-slate-500"
        title="Settings"
      >
        <Settings className="h-5 w-5" />
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm animate-in fade-in"
        onClick={() => setOpen(false)}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-2xl bg-white dark:bg-slate-900 rounded-[32px] shadow-2xl overflow-hidden flex flex-col md:flex-row h-[500px] animate-in zoom-in-95 duration-300">
        
        {/* Sidebar Nav */}
        <div className="w-full md:w-48 bg-slate-50 dark:bg-slate-800/50 p-6 flex flex-col gap-2 border-r border-slate-100 dark:border-slate-800">
          <div className="mb-4">
             <h2 className="text-xs font-black uppercase tracking-[0.2em] text-slate-400">Settings</h2>
          </div>
          
          <TabButton 
            active={activeTab === 'general'} 
            onClick={() => setActiveTab('general')} 
            icon={<Cog className="h-4 w-4" />} 
            label="General" 
          />
          <TabButton 
            active={activeTab === 'advanced'} 
            onClick={() => setActiveTab('advanced')} 
            icon={<Globe className="h-4 w-4" />} 
            label="Advanced" 
          />
          <TabButton 
            active={activeTab === 'about'} 
            onClick={() => setActiveTab('about')} 
            icon={<Info className="h-4 w-4" />} 
            label="About" 
          />
          
          <div className="mt-auto">
             <button 
                onClick={() => setOpen(false)}
                className="w-full py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl text-xs font-bold transition-all active:scale-95"
             >
               Done
             </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 p-8 overflow-y-auto overflow-x-hidden">
           {activeTab === 'general' && (
             <div className="space-y-8 animate-in slide-in-from-right-4">
                <div className="space-y-4">
                   <h3 className="text-sm font-bold text-slate-900 dark:text-white">Appearance</h3>
                   <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
                      <div className="flex items-center gap-3">
                         <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
                           {darkMode ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
                         </div>
                         <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Dark Mode</span>
                      </div>
                      <button 
                        onClick={toggleTheme}
                        className={cn(
                          "relative w-10 h-5 rounded-full transition-colors",
                          darkMode ? "bg-blue-500" : "bg-slate-300"
                        )}
                      >
                         <div className={cn(
                           "absolute top-1 left-1 h-3 w-3 bg-white rounded-full transition-transform",
                           darkMode ? "translate-x-5" : "translate-x-0"
                         )} />
                      </button>
                   </div>
                </div>

                <div className="space-y-4">
                   <h3 className="text-sm font-bold text-slate-900 dark:text-white">Privacy</h3>
                   <div className="flex items-center gap-3 p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
                      <ShieldCheck className="h-5 w-5 text-green-500" />
                      <div className="flex flex-col">
                         <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Zero-Retention Mode</span>
                         <span className="text-[10px] text-slate-500 font-medium">Conversations are not stored on server</span>
                      </div>
                   </div>
                </div>
             </div>
           )}

           {activeTab === 'advanced' && (
             <div className="space-y-6 animate-in slide-in-from-right-4">
                <div className="space-y-3">
                   <h3 className="text-sm font-bold text-slate-900 dark:text-white">Backend Configuration</h3>
                   <p className="text-xs text-slate-500 leading-relaxed font-medium">
                     Override the default API endpoint for local development or custom deployments.
                   </p>
                </div>
                
                <div className="space-y-2">
                   <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">API Endpoint URL</label>
                   <div className="flex gap-2">
                      <div className="relative flex-1">
                         <Database className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
                         <input 
                           type="text" 
                           value={apiUrl}
                           onChange={(e) => setApiUrl(e.target.value)}
                           className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs font-mono text-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                         />
                      </div>
                      <button className="px-3 py-2 bg-slate-100 dark:bg-slate-800 rounded-xl text-[10px] font-bold uppercase text-slate-500 hover:text-blue-500 transition-colors">Apply</button>
                   </div>
                </div>
             </div>
           )}

           {activeTab === 'about' && (
             <div className="space-y-8 animate-in slide-in-from-right-4">
                <div className="flex flex-col items-center text-center space-y-4">
                   <div className="h-20 w-20 rounded-[28px] bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-xl shadow-blue-500/20">
                      <ShieldCheck className="h-10 w-10 text-white" />
                   </div>
                   <div>
                      <h4 className="text-lg font-black text-slate-900 dark:text-white">LegalFinanceAI</h4>
                      <p className="text-xs font-bold text-blue-500 uppercase tracking-widest">Version 1.0.4-Stable</p>
                   </div>
                </div>

                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                   <div className="py-3 flex justify-between items-center text-xs">
                      <span className="text-slate-500 font-medium">System Status</span>
                      <span className="px-2 py-0.5 rounded-full bg-green-100 dark:bg-green-500/10 text-green-600 font-bold uppercase tracking-tight">Healthy</span>
                   </div>
                   <div className="py-3 flex justify-between items-center text-xs">
                      <span className="text-slate-500 font-medium">Provider</span>
                      <span className="text-slate-900 dark:text-white font-bold">Nikil-R / Legal_Finance_RAG</span>
                   </div>
                   <div className="py-3 flex justify-between items-center text-xs">
                      <span className="text-slate-500 font-medium">Legal Disclaimer</span>
                      <span className="text-blue-500 font-bold hover:underline cursor-pointer">View Terms</span>
                   </div>
                </div>
             </div>
           )}
        </div>
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon, label }: any) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 px-4 py-3 rounded-2xl text-xs font-bold transition-all",
        active 
          ? "bg-white dark:bg-slate-800 text-blue-500 shadow-sm shadow-slate-200 dark:shadow-none" 
          : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-700 dark:hover:text-slate-300"
      )}
    >
      {icon}
      {label}
    </button>
  );
}
