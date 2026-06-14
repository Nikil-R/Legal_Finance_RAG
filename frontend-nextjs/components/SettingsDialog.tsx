'use client';

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Settings, X, Moon, Sun, Monitor, Info, ShieldCheck, Globe, Database, Cog } from 'lucide-react';
import { cn } from '@/lib/utils';

export function SettingsDialog() {
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'general' | 'advanced' | 'about'>('general');
  const [darkMode, setDarkMode] = useState(true);
  const [apiUrl, setApiUrl] = useState('');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Initial sync with document class and env variable
    setDarkMode(document.documentElement.classList.contains('dark'));
    setApiUrl(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');
  }, []);

  const toggleTheme = () => {
    const next = !darkMode;
    setDarkMode(next);
    if (next) document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
  };

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors text-slate-500"
        title="Settings"
      >
        <Settings className="h-5 w-5" />
      </button>

      {open && mounted && createPortal(
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-[#0A0A0A]/80 backdrop-blur-sm animate-in fade-in"
            onClick={() => setOpen(false)}
          />
          
          {/* Modal */}
          <div className="relative w-full max-w-2xl bg-[#111827] border border-border rounded-[32px] shadow-2xl overflow-hidden flex flex-col md:flex-row h-[500px] animate-in zoom-in-95 duration-300">
            
            {/* Sidebar Nav */}
            <div className="w-full md:w-48 bg-[#111827] p-6 flex flex-col gap-2 border-r border-border">
          <div className="mb-4">
             <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted">Settings</h2>
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
                className="w-full py-2 bg-primary text-[#0A0A0A] rounded-xl text-xs font-bold transition-all hover:brightness-110 active:scale-95 shadow-lg shadow-primary/20"
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
                   <h3 className="text-sm font-bold text-foreground">Appearance</h3>
                   <div className="flex items-center justify-between p-4 rounded-2xl bg-[#1F2937] border border-border">
                      <div className="flex items-center gap-3">
                         <div className="p-2 rounded-lg bg-primary/10 text-primary">
                           {darkMode ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
                         </div>
                         <span className="text-xs font-bold text-foreground">Dark Mode</span>
                      </div>
                      <button 
                        onClick={toggleTheme}
                        className={cn(
                          "relative w-10 h-5 rounded-full transition-colors",
                          darkMode ? "bg-primary" : "bg-muted"
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
                   <h3 className="text-sm font-bold text-foreground">Privacy</h3>
                   <div className="flex items-center gap-3 p-4 rounded-2xl bg-[#1F2937] border border-border">
                      <ShieldCheck className="h-5 w-5 text-green-500" />
                      <div className="flex flex-col">
                         <span className="text-xs font-bold text-foreground">Zero-Retention Mode</span>
                         <span className="text-[10px] text-muted font-medium">Conversations are not stored on server</span>
                      </div>
                   </div>
                </div>
             </div>
           )}

           {activeTab === 'advanced' && (
             <div className="space-y-6 animate-in slide-in-from-right-4">
                 <div className="space-y-3">
                   <h3 className="text-sm font-bold text-foreground">Backend Configuration</h3>
                   <p className="text-xs text-muted leading-relaxed font-medium">
                     Override the default API endpoint for local development or custom deployments.
                   </p>
                </div>
                
                <div className="space-y-2">
                   <label className="text-[10px] font-bold uppercase tracking-wider text-muted">API Endpoint URL</label>
                   <div className="flex gap-2">
                      <div className="relative flex-1">
                         <Database className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted" />
                         <input 
                           type="text" 
                           value={apiUrl}
                           onChange={(e) => setApiUrl(e.target.value)}
                           className="w-full bg-[#1F2937] border border-border rounded-xl pl-10 pr-4 py-2 text-xs font-mono text-foreground focus:outline-none focus:border-primary/50 transition-all"
                         />
                      </div>
                      <button className="px-3 py-2 bg-[#1F2937] rounded-xl text-[10px] font-bold uppercase text-muted hover:text-primary border border-border transition-colors">Apply</button>
                   </div>
                </div>
             </div>
           )}

           {activeTab === 'about' && (
             <div className="space-y-8 animate-in slide-in-from-right-4">
                 <div className="flex flex-col items-center text-center space-y-4">
                   <div className="h-20 w-20 rounded-[28px] bg-gradient-to-br from-[#1F2937] to-[#111827] flex items-center justify-center shadow-xl shadow-primary/5 border border-primary/20">
                      <ShieldCheck className="h-10 w-10 text-primary" />
                   </div>
                   <div>
                      <h4 className="text-lg font-black text-foreground">LegalFinanceAI</h4>
                      <p className="text-xs font-bold text-primary uppercase tracking-widest">Version 1.0.4-Stable</p>
                   </div>
                </div>

                <div className="divide-y divide-border">
                   <div className="py-3 flex justify-between items-center text-xs">
                      <span className="text-muted font-medium">System Status</span>
                      <span className="px-2 py-0.5 rounded-full bg-green-500/10 text-green-500 font-bold uppercase tracking-tight">Healthy</span>
                   </div>
                   <div className="py-3 flex justify-between items-center text-xs">
                      <span className="text-muted font-medium">Provider</span>
                      <span className="text-foreground font-bold">Nikil-R / Legal_Finance_RAG</span>
                   </div>
                   <div className="py-3 flex justify-between items-center text-xs">
                      <span className="text-muted font-medium">Legal Disclaimer</span>
                      <span className="text-primary font-bold hover:underline cursor-pointer">View Terms</span>
                   </div>
                </div>
             </div>
           )}
        </div>
        </div>
        </div>,
        document.body
      )}
    </>
  );
}

function TabButton({ active, onClick, icon, label }: any) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 px-4 py-3 rounded-2xl text-xs font-bold transition-all",
        active 
          ? "bg-[#1F2937] text-primary" 
          : "text-muted hover:bg-[#1F2937]/50 hover:text-foreground"
      )}
    >
      {icon}
      {label}
    </button>
  );
}
