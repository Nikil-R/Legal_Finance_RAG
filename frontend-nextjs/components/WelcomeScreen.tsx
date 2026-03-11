'use client';

import { ArrowRight, Lightbulb, FileText, Scale, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface WelcomeScreenProps {
  onStarterClick: (question: string) => void;
}

const starterQuestions = [
  {
    icon: Scale,
    title: 'Legal Analysis',
    description: 'Analyze contract clauses and legal documents',
    example: 'What are the key liability clauses in this contract?',
  },
  {
    icon: TrendingUp,
    title: 'Financial Insights',
    description: 'Extract and analyze financial data',
    example: 'What is the revenue growth rate over the past year?',
  },
  {
    icon: FileText,
    title: 'Document Review',
    description: 'Review and summarize documents quickly',
    example: 'Summarize the key terms and conditions',
  },
  {
    icon: Lightbulb,
    title: 'Compliance Check',
    description: 'Verify compliance with regulations',
    example: 'Does this document comply with current regulations?',
  },
];

export function WelcomeScreen({ onStarterClick }: WelcomeScreenProps) {
  return (
    <div className="flex-grow flex flex-col items-center justify-center p-6 md:p-12 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-slate-950 dark:to-slate-900">
      <div className="max-w-3xl w-full space-y-12">
        {/* Header Section */}
        <div className="text-center space-y-4">
          <div className="flex justify-center mb-6">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-blue-700 shadow-lg">
              <Lightbulb className="h-8 w-8 text-white" />
            </div>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white">
            Welcome to LegalFinanceAI
          </h1>

          <p className="text-lg text-gray-600 dark:text-slate-400 max-w-xl mx-auto">
            Your intelligent assistant for legal and financial document analysis.
            Upload your documents and ask questions to get instant insights.
          </p>
        </div>

        {/* Quick Start Section */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-gray-600 dark:text-slate-400 uppercase tracking-wider text-center">
            Try These Questions
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {starterQuestions.map((question, index) => {
              const Icon = question.icon;
              return (
                <button
                  key={index}
                  onClick={() => onStarterClick(question.example)}
                  className="group relative rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 text-left transition-all hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-lg dark:hover:bg-slate-750"
                >
                  {/* Gradient Overlay on Hover */}
                  <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-blue-600/0 to-blue-600/0 group-hover:from-blue-600/5 group-hover:to-blue-600/10 transition-all" />

                  <div className="relative space-y-3">
                    {/* Icon and Title Row */}
                    <div className="flex items-start justify-between">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-500/10">
                        <Icon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                      </div>
                      <ArrowRight className="h-5 w-5 text-gray-400 dark:text-slate-500 transition-colors group-hover:text-blue-600 dark:group-hover:text-blue-400 transform group-hover:translate-x-1" />
                    </div>

                    {/* Title */}
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {question.title}
                    </h3>

                    {/* Description */}
                    <p className="text-sm text-gray-600 dark:text-slate-400">
                      {question.description}
                    </p>

                    {/* Example in Small Text */}
                    <p className="text-xs text-gray-500 dark:text-slate-500 italic">
                      "{question.example}"
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Help Section */}
        <div className="rounded-lg bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/30 p-6">
          <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">
            Getting Started
          </h3>
          <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
            <li className="flex gap-2">
              <span>1.</span>
              <span>Upload your legal or financial documents using the sidebar</span>
            </li>
            <li className="flex gap-2">
              <span>2.</span>
              <span>Ask specific questions about your documents</span>
            </li>
            <li className="flex gap-2">
              <span>3.</span>
              <span>
                Get instant AI-powered analysis with citations to source documents
              </span>
            </li>
          </ul>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Documents Supported', value: '∞' },
            { label: 'Avg. Response Time', value: '< 5s' },
            { label: 'Accuracy Rate', value: '95%+' },
          ].map((stat, index) => (
            <div
              key={index}
              className="rounded-lg border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-800 p-4 text-center"
            >
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stat.value}
              </p>
              <p className="text-xs text-gray-600 dark:text-slate-500 mt-1">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
