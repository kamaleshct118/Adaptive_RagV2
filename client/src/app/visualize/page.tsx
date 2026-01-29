'use client';

import React from 'react';
import Link from 'next/link';

interface StepProps {
    number: number;
    title: string;
    description: string;
    isLast?: boolean;
}

const VizStep: React.FC<StepProps> = ({ number, title, description, isLast }) => (
    <>
        <div className="viz-step">
            <div className="viz-step-number">{number}</div>
            <div className="viz-step-info">
                <h3 className="viz-step-title">{title}</h3>
                <p className="viz-step-desc">{description}</p>
            </div>
        </div>
        {!isLast && <div className="viz-connector"></div>}
    </>
);

export default function Visualize() {
    return (
        <div className="app-container">
            {/* Header */}
            <header className="header">
                <div className="header-logo">
                    <div className="header-logo-icon">🏥</div>
                    <div>
                        <h1 className="header-title">Adaptive RAG Assistant</h1>
                        <p className="header-subtitle">Architecture Visualization</p>
                    </div>
                </div>
                <nav className="header-nav">
                    <Link href="/" className="nav-link">Chat</Link>
                    <Link href="/visualize" className="nav-link active">Architecture</Link>
                </nav>
            </header>

            <main className="chat-container viz-container">
                <div className="viz-title">
                    <div className="cycle-badge">
                        <span className="cycle-icon">🔄</span>
                        10-Phase Pipeline
                    </div>
                    <h1>Adaptive RAG Logic</h1>
                    <p className="welcome-subtitle">
                        An advanced, self-correcting retrieval system that ensures medical accuracy through multiple validation layers.
                    </p>
                </div>

                <div className="viz-flow">
                    <VizStep
                        number={1}
                        title="Query Analysis"
                        description="The system deconstructs your query to identify medical intent, category, and desired tone."
                    />
                    <VizStep
                        number={2}
                        title="Relevance Check"
                        description="A guardrail phase that ensures the query is actually about a medical topic."
                    />
                    <VizStep
                        number={3}
                        title="Safety Validation"
                        description="Ensures that any internal query rewriting hasn't changed the clinical meaning."
                    />
                    <VizStep
                        number={4}
                        title="Central Control Node"
                        description="The brain of the pipeline that decides the retrieval strategy based on analysis."
                    />
                    <VizStep
                        number={5}
                        title="Document Retrieval"
                        description="Fetches the most relevant medical guideline chunks using FAISS vector search."
                    />
                    <VizStep
                        number={6}
                        title="Retrieval Grading"
                        description="Filters out retrieved chunks that aren't perfectly relevant to prevent hallucinations."
                    />
                    <VizStep
                        number={7}
                        title="Answer Generation"
                        description="Synthesizes a structured response using ONLY the verified medical context."
                    />
                    <VizStep
                        number={8}
                        title="Hallucination Check"
                        description="Verifies the generated answer against the source chunks to ensure factual loyalty."
                    />
                    <VizStep
                        number={9}
                        title="Final Relevance"
                        description="Final check to ensure the generated answer actually addresses your original question."
                    />
                    <VizStep
                        number={10}
                        title="Orchestration Loop"
                        description="If any check fails, the system automatically loops back and tries a different strategy."
                        isLast={true}
                    />
                </div>

                <div style={{ marginTop: 'var(--space-12)', textAlign: 'center' }}>
                    <Link href="/" className="submit-button" style={{ display: 'inline-flex', textDecoration: 'none', width: 'auto', padding: '0 var(--space-8)' }}>
                        Back to Chat
                    </Link>
                </div>
            </main>
        </div>
    );
}
