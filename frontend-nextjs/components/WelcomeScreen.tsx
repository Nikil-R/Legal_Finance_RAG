'use client';

import { ArrowRight, Zap, Target, PieChart, ShieldCheck, Flame } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WelcomeScreenProps {
  onStarterClick: (question: string) => void;
}

const STARTER_CARDS = [
  {
    icon: Target,
    title: 'Indian Budget 2026',
    description: 'Explain key highlights and fiscal allocations.',
    example: 'Summarize the key highlights and allocations for infrastructure in the 2026 Budget.',
    color: 'blue'
  },
  {
    icon: PieChart,
    title: 'Tax Policy Analysis',
    description: 'Analyze changes in direct and indirect taxes.',
    example: 'What are the major changes in GST and Income Tax rates for the next fiscal year?',
    color: 'cyan'
  },
  {
    icon: ShieldCheck,
    title: 'Legal Compliance',
    description: 'Verify document adherence to new regulations.',
    example: 'Are there any new compliance requirements for fintech startups mentioned in the budget?',
    color: 'indigo'
  },
  {
    icon: Flame,
    title: 'Market Impact',
    description: 'Assess the impact on specific industry sectors.',
    example: 'How does the current budget impact the renewable energy sector in India?',
    color: 'amber'
  },
];

export function WelcomeScreen({ onStarterClick }: WelcomeScreenProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 lg:p-12 overflow-y-auto">
      <div className="max-w-4xl w-full">
        {/* Hero Section */}
        <div className="text-center space-y-8 mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-600 dark:text-blue-400 text-[10px] font-bold uppercase tracking-widest animate-pulse-soft">
            <Zap className="h-3 w-3" /> AI-Powered Intelligence
          </div>
          
          <div className="space-y-4">
            <h1 className="text-4xl md:text-6xl font-black tracking-tight text-slate-900 dark:text-white leading-[1.1]">
              Legal & Financial <br />
              <span className="brand-gradient">RAG Assistant</span>
            </h1>
            <p className="text-base md:text-lg text-slate-500 dark:text-slate-400 max-w-2xl mx-auto font-medium leading-relaxed">
              Upload your documents and get instant, cited answers based on the 
              latest Indian budgetary and legal frameworks.
            </p>
          </div>
        </div>

        {/* Categories / Starters */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {STARTER_CARDS.map((card, idx) => (
            <button
              key={idx}
              onClick={() => onStarterClick(card.example)}
              className={cn(
                "group relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 p-6 text-left transition-all",
                "hover:border-blue-500/50 hover:shadow-2xl hover:shadow-blue-500/10 hover:-translate-y-1",
                "animate-message"
              )}
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                <card.icon className="h-24 w-24" />
              </div>
              
              <div className="relative z-10 space-y-4">
                <div className="flex items-center justify-between">
                  <div className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-xl transition-transform group-hover:scale-110 shadow-lg",
                    card.color === 'blue' ? "bg-blue-500 text-white shadow-blue-500/20" :
                    card.color === 'cyan' ? "bg-cyan-500 text-white shadow-cyan-500/20" :
                    card.color === 'indigo' ? "bg-indigo-500 text-white shadow-indigo-500/20" :
                    "bg-amber-500 text-white shadow-amber-500/20"
                  )}>
                    <card.icon className="h-5 w-5" />
                  </div>
                  <ArrowRight className="h-5 w-5 text-slate-300 dark:text-slate-700 group-hover:text-blue-500 transition-colors" />
                </div>
                
                <div>
                  <h3 className="font-bold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-500 mt-1 font-medium">
                    {card.description}
                  </p>
                </div>
                
                <div className="pt-2">
                  <p className="text-[10px] text-slate-400 italic">
                    "{card.example}"
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Trust/Status Bar */}
        <div className="mt-16 pt-8 border-t border-slate-100 dark:border-slate-800/50 flex flex-wrap items-center justify-center gap-8 md:gap-16 opacity-50 grayscale hover:grayscale-0 transition-all duration-700">
           <div className="flex flex-col items-center">
              <span className="text-2xl font-black text-slate-900 dark:text-white">4.3%</span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Target Deficit</span>
           </div>
           <div className="flex flex-col items-center">
              <span className="text-2xl font-black text-slate-900 dark:text-white">BE'26</span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Budget Estimates</span>
           </div>
           <div className="flex flex-col items-center">
              <span className="text-2xl font-black text-slate-900 dark:text-white">99%</span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">RAG Accuracy</span>
           </div>
        </div>
      </div>
    </div>
  );
}
