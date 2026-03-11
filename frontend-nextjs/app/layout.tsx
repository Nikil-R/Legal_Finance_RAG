import type { Metadata } from 'next';
import './globals.css';
import { Header } from '@/components/Header';
import { ToastProvider } from '@/components/ToastProvider';

export const metadata: Metadata = {
  title: 'LegalFinance AI - Indian Legal & Finance Research Assistant',
  description:
    'AI-powered research assistant for Indian legal and financial topics. Ask questions about taxes, law, and more.',
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
    <html lang="en" className="scroll-smooth">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="bg-gray-50 dark:bg-slate-950 text-gray-900 dark:text-slate-100 antialiased">
        <ToastProvider>
          <div className="flex flex-col h-screen">
            <Header />
            <main className="flex-1 overflow-hidden bg-gray-50 dark:bg-slate-950">
              {children}
            </main>
          </div>
        </ToastProvider>
      </body>
    </html>
  );
}
