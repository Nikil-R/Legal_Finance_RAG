import type { Metadata } from 'next';
import './globals.css';
import { ToastProvider } from '@/components/ToastProvider';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'LegalFinanceAI - Indian Legal & Finance RAG Engine',
  description:
    'Advanced AI-powered research assistant for Indian legal and financial documents. Get cited answers with compliance checks.',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth dark">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0" />
        <meta name="theme-color" content="#020617" />
      </head>
      <body className={`${inter.className} bg-background text-foreground antialiased overflow-hidden h-screen`}>
        <ToastProvider>
           {children}
        </ToastProvider>
      </body>
    </html>
  );
}
