'use client';

import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import Link from 'next/link';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    category?: string;
    tone?: string;
    isFallback?: boolean;
    timestamp: Date;
}

interface ApiResponse {
    answer: string;
    category: string;
    tone: string;
    is_fallback: boolean;
    success: boolean;
    logs?: string[];
}

const EXAMPLE_QUERIES = [
    "What are first-line antibiotics for pneumonia?",
    "Explain antibiotic resistance mechanisms",
    "When should we use carbapenem antibiotics?",
];

export default function Home() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [serverStatus, setServerStatus] = useState<'online' | 'offline' | 'checking'>('checking');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Check server health on mount
    useEffect(() => {
        checkServerHealth();
    }, []);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    }, [inputValue]);

    const checkServerHealth = async () => {
        try {
            const response = await fetch('/api/health');
            if (response.ok) {
                setServerStatus('online');
            } else {
                setServerStatus('offline');
            }
        } catch (error) {
            setServerStatus('offline');
        }
    };

    const sendMessage = async (query: string) => {
        if (!query.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: query.trim(),
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query.trim() }),
            });

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data: ApiResponse = await response.json();

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.answer,
                category: data.category,
                tone: data.tone,
                isFallback: data.is_fallback,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: '❌ Unable to connect to the server. Please make sure the backend is running on port 8000.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
            setServerStatus('offline');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        sendMessage(inputValue);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(inputValue);
        }
    };

    return (
        <div className="app-container">
            {/* Header */}
            <header className="header">
                <div className="header-logo">
                    <div className="header-logo-icon">🏥</div>
                    <div>
                        <h1 className="header-title">Adaptive RAG Assistant</h1>
                        <p className="header-subtitle">Medical Guideline Intelligence</p>
                    </div>
                </div>
                <nav className="header-nav">
                    <Link href="/" className="nav-link active">Chat</Link>
                    <Link href="/visualize" className="nav-link">Architecture</Link>
                </nav>
                <div className="header-status">
                    <span className={`status-dot ${serverStatus !== 'online' ? 'status-offline' : ''}`}
                        style={{ background: serverStatus === 'online' ? 'var(--success)' : serverStatus === 'checking' ? 'var(--warning)' : 'var(--error)' }} />
                    {serverStatus === 'online' ? 'Connected' : serverStatus === 'checking' ? 'Checking...' : 'Offline'}
                </div>
            </header>

            {/* Chat Container */}
            <main className="chat-container">
                {/* Messages Area */}
                <div className="messages-area">
                    {messages.length === 0 ? (
                        <div className="welcome-message">
                            <div className="welcome-icon">🏥</div>
                            <h2 className="welcome-title">Welcome to Adaptive RAG</h2>
                            <p className="welcome-subtitle">
                                Ask me anything about antimicrobial stewardship, antibiotic guidelines, or infection management.
                            </p>
                            <div className="example-queries">
                                {EXAMPLE_QUERIES.map((query, idx) => (
                                    <button
                                        key={idx}
                                        className="example-query"
                                        onClick={() => sendMessage(query)}
                                        disabled={isLoading}
                                    >
                                        {query}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ) : (
                        messages.map((message) => (
                            <div
                                key={message.id}
                                className={`message message-${message.role}`}
                            >
                                <div className="message-content">
                                    {message.role === 'assistant' ? (
                                        <ReactMarkdown>{message.content}</ReactMarkdown>
                                    ) : (
                                        message.content
                                    )}
                                </div>
                                {message.role === 'assistant' && (message.category || message.tone) && (
                                    <div className="message-meta">
                                        {message.category && (
                                            <span className="message-category">{message.category}</span>
                                        )}
                                        {message.tone && (
                                            <span className="message-tone">{message.tone}</span>
                                        )}
                                        {message.isFallback && (
                                            <div className="fallback-notice">
                                                ⚠️ Fallback response (limited KB coverage)
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))
                    )}

                    {isLoading && (
                        <div className="message message-assistant">
                            <div className="loading-indicator">
                                <div className="loading-dots">
                                    <span className="loading-dot"></span>
                                    <span className="loading-dot"></span>
                                    <span className="loading-dot"></span>
                                </div>
                                <span className="loading-text">Thinking...</span>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="input-area">
                    <form className="input-form" onSubmit={handleSubmit}>
                        <div className="input-wrapper">
                            <textarea
                                ref={textareaRef}
                                className="input-field"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask a medical question..."
                                disabled={isLoading}
                                rows={1}
                            />
                        </div>
                        <button
                            type="submit"
                            className="submit-button"
                            disabled={isLoading || !inputValue.trim()}
                        >
                            <svg
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                                />
                            </svg>
                        </button>
                    </form>
                </div>
            </main>
        </div>
    );
}
