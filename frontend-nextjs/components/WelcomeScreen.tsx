'use client';

import { ArrowRight, Zap, Target, PieChart, ShieldCheck, Flame } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WelcomeScreenProps {
  onStarterClick: (question: string) => void;
}

const STARTER_CARDS = [
  {
    icon: Target,
    title: 'Tax Calculation',
    description: 'Calculate income tax for FY 2026-27.',
    example: 'Calculate tax on ₹15,00,000 income in the new regime for FY 2026-27.',
    color: 'blue'
  },
  {
    icon: PieChart,
    title: 'GST Rate Search',
    description: 'Look up GST rates and HSN codes.',
    example: 'What is the GST rate and HSN code for restaurant services?',
    color: 'cyan'
  },
  {
    icon: ShieldCheck,
    title: 'Budget Analysis',
    description: 'Compare budget figures and fiscal targets.',
    example: 'Compare the fiscal deficit targets of 2025-26 and 2026-27.',
    color: 'indigo'
  },
  {
    icon: Flame,
    title: 'Comparison Mode',
    description: 'Compare legal scenarios side-by-side.',
    example: 'Compare the tax implications of the Old vs New Regime for an income of ₹20 Lakhs.',
    color: 'amber'
  },
];

export function WelcomeScreen({ onStarterClick }: WelcomeScreenProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 lg:p-12 overflow-y-auto">
      <div className="max-w-4xl w-full">
        {/* Hero Section */}
        <div className="text-center space-y-8 mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-[10px] font-bold uppercase tracking-widest animate-pulse-soft">
            <Zap className="h-3 w-3" /> AI-Powered Intelligence
          </div>
          
          <div className="space-y-4">
            <h1 className="text-4xl md:text-6xl font-black tracking-tight text-foreground leading-[1.1]">
              Legal & Financial <br />
              <span className="brand-gradient">RAG Assistant</span>
            </h1>
            <p className="text-base md:text-lg text-muted max-w-2xl mx-auto font-medium leading-relaxed">
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
                "group relative overflow-hidden rounded-2xl border border-border bg-card p-6 text-left transition-all",
                "hover:border-primary/50 hover:shadow-2xl hover:shadow-primary/10 hover:-translate-y-1",
                "animate-message"
              )}
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                <card.icon className="h-24 w-24 text-primary" />
              </div>
              
              <div className="relative z-10 space-y-4">
                <div className="flex items-center justify-between">
                  <div className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-xl transition-transform group-hover:scale-110 shadow-lg",
                    "bg-background border border-primary/20 text-primary shadow-primary/10"
                  )}>
                    <card.icon className="h-5 w-5" />
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted group-hover:text-primary transition-colors" />
                </div>
                
                <div>
                  <h3 className="font-bold text-foreground group-hover:text-primary transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-xs text-muted mt-1 font-medium">
                    {card.description}
                  </p>
                </div>
                
                <div className="pt-2">
                  <p className="text-[10px] text-muted italic">
                    "{card.example}"
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Trust/Status Bar */}
        <div className="mt-16 pt-8 border-t border-border flex flex-wrap items-center justify-center gap-8 md:gap-16 opacity-50 grayscale hover:grayscale-0 transition-all duration-700">
           <div className="flex flex-col items-center">
              <span className="text-2xl font-black text-foreground">4.3%</span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-muted">Target Deficit</span>
           </div>
           <div className="flex flex-col items-center">
              <span className="text-2xl font-black text-foreground">BE'26</span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-muted">Budget Estimates</span>
           </div>
           <div className="flex flex-col items-center">
              <span className="text-2xl font-black text-foreground">99%</span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-muted">RAG Accuracy</span>
           </div>
        </div>
      </div>
    </div>
  );
}
