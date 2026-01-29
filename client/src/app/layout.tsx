import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'Adaptive RAG Assistant | Medical Guidelines',
    description: 'AI-powered medical guideline assistant with verified, citation-backed responses for antimicrobial stewardship.',
    keywords: ['medical AI', 'RAG', 'antimicrobial stewardship', 'medical guidelines', 'healthcare AI'],
    authors: [{ name: 'Adaptive RAG Team' }],
    openGraph: {
        title: 'Adaptive RAG Assistant',
        description: 'AI-powered medical guideline assistant',
        type: 'website',
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <head>
                <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏥</text></svg>" />
            </head>
            <body className={inter.className}>{children}</body>
        </html>
    );
}
