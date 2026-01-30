'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';

interface TraceStepData {
    name: string;
    status: 'completed' | 'failed' | 'pending';
    data?: any;
}

interface TraceCycle {
    cycle: number;
    analysis: any;
    steps: TraceStepData[];
}

interface StepProps {
    number: number;
    title: string;
    description: string;
    traceData?: TraceStepData;
    isActive: boolean;
    onClick: () => void;
    isLastInRow?: boolean;
}

const VizStep: React.FC<StepProps> = ({ number, title, description, traceData, isActive, onClick, isLastInRow }) => {
    const getStatusColor = () => {
        if (!traceData) return 'var(--gray-700)';
        if (traceData.status === 'completed') return 'var(--success)';
        if (traceData.status === 'failed') return 'var(--error)';
        return 'var(--warning)';
    };

    return (
        <div className="viz-step-wrapper">
            <div
                className={`viz-step ${isActive ? 'viz-step-active' : ''} ${traceData ? 'viz-step-data' : ''}`}
                onClick={onClick}
                style={{ borderColor: isActive ? 'var(--blue-500)' : 'transparent' }}
            >
                <div className="viz-step-number" style={{ background: getStatusColor() }}>
                    {traceData?.status === 'completed' ? '✓' : traceData?.status === 'failed' ? '✗' : number}
                </div>
                <div className="viz-step-info">
                    <h3 className="viz-step-title">{title}</h3>
                </div>
            </div>
            {!isLastInRow && (
                <div className="viz-connector-h"></div>
            )}
        </div>
    );
};

export default function Visualize() {
    const [query, setQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [trace, setTrace] = useState<TraceCycle[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [selectedStep, setSelectedStep] = useState<number>(0);

    const runTrace = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        if (!query.trim() || isLoading) return;

        setIsLoading(true);
        setError(null);
        setTrace(null);

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query.trim() }),
            });

            if (!response.ok) throw new Error('Failed to fetch trace');

            const data = await response.json();
            if (data.detailed_trace) {
                setTrace(data.detailed_trace);
            } else {
                setError("Backend did not provide a detailed trace.");
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    const steps = [
        { title: "Query Analysis", desc: "Deconstructing query to identify medical intent.", trace: "Query Analysis" },
        { title: "Domain Relevance", desc: "Verifying medical domain relevance.", trace: "Query Analysis" },
        { title: "Safety Validation", desc: "Checking clinical integrity.", trace: "Query Analysis" },
        { title: "Central Control", desc: "Managing execution flow.", trace: "Query Analysis" },
        { title: "Doc Retrieval", desc: "Fetching knowledge base chunks.", trace: "Document Retrieval" },
        { title: "KB Coverage", desc: "Checking coverage sufficiency.", trace: "KB Coverage Guard" },
        { title: "Retrieval Grading", desc: "Scoring chunk relevance.", trace: "Retrieval Grading" },
        { title: "Answer Gen", desc: "Synthesizing medical response.", trace: "Answer Generation" },
        { title: "Hallucination Check", desc: "Fact-checking against sources.", trace: "Hallucination Check" },
        { title: "Final Relevance", desc: "Ensuring user intent is met.", trace: "Final Relevance Check" },
    ];

    const getStepTrace = (stepName: string): TraceStepData | undefined => {
        if (!trace || trace.length === 0) return undefined;
        const lastCycle = trace[trace.length - 1];
        return lastCycle.steps.find((s: TraceStepData) => s.name === stepName);
    };

    const selectedTraceData = getStepTrace(steps[selectedStep].trace);

    return (
        <div className="app-container" style={{ padding: 'var(--space-2)' }}>
            <header className="header" style={{ marginBottom: 'var(--space-2)', padding: 'var(--space-2) var(--space-4)' }}>
                <div className="header-logo">
                    <div className="header-logo-icon" style={{ width: '30px', height: '30px', fontSize: '1rem' }}>🏥</div>
                    <div>
                        <h1 className="header-title" style={{ fontSize: '1.1rem' }}>Adaptive RAG</h1>
                    </div>
                </div>
                <nav className="header-nav">
                    <Link href="/" className="nav-link">Chat</Link>
                    <Link href="/visualize" className="nav-link active">Pipeline</Link>
                </nav>
            </header>

            <main className="chat-container viz-container" style={{ overflowY: 'hidden', padding: 'var(--space-4)' }}>
                <form className="input-form" onSubmit={runTrace} style={{ maxWidth: '800px', margin: '0 auto var(--space-4) auto' }}>
                    <div className="input-wrapper">
                        <input
                            type="text"
                            className="input-field"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Trace a medical query..."
                            disabled={isLoading}
                            style={{ borderRadius: 'var(--radius-full)', padding: 'var(--space-2) var(--space-6)', minHeight: '40px', background: 'var(--blue-950)' }}
                        />
                    </div>
                    <button type="submit" className="submit-button" disabled={isLoading || !query.trim()} style={{ borderRadius: 'var(--radius-full)', height: '40px', minWidth: '80px', padding: '0 var(--space-4)' }}>
                        {isLoading ? '...' : 'Analyze'}
                    </button>
                </form>

                <div className="pipeline-grid">
                    <div className="pipeline-row">
                        {steps.slice(0, 5).map((step, i) => (
                            <VizStep
                                key={i}
                                number={i + 1}
                                title={step.title}
                                description={step.desc}
                                traceData={getStepTrace(step.trace)}
                                isActive={selectedStep === i}
                                onClick={() => setSelectedStep(i)}
                                isLastInRow={i === 4}
                            />
                        ))}
                    </div>

                    <div className="pipeline-row-connector">
                        <div className="connector-vertical"></div>
                    </div>

                    <div className="pipeline-row row-reverse">
                        {steps.slice(5, 10).map((step, i) => (
                            <VizStep
                                key={i + 5}
                                number={i + 6}
                                title={step.title}
                                description={step.desc}
                                traceData={getStepTrace(step.trace)}
                                isActive={selectedStep === i + 5}
                                onClick={() => setSelectedStep(i + 5)}
                                isLastInRow={i === 4}
                            />
                        ))}
                    </div>
                </div>

                <div className="inspector-screen">
                    <div className="screen-header">
                        <div className="screen-titling">
                            <span className="screen-icon">📡</span>
                            <h3>PROCESSS_INSPECTOR: {steps[selectedStep].title.toUpperCase()}</h3>
                        </div>
                        <div className="screen-status">
                            {selectedTraceData?.status || 'IDLE'}
                        </div>
                    </div>
                    <div className="screen-content">
                        {isLoading ? (
                            <div className="screen-loading">
                                <div className="scanner-line"></div>
                                <p>INITIALIZING PIPELINE TRACE...</p>
                            </div>
                        ) : selectedTraceData ? (
                            <div className="trace-details">
                                <div className="trace-info-grid">
                                    <div className="info-item">
                                        <label>PHASE</label>
                                        <span>{selectedStep + 1}/10</span>
                                    </div>
                                    <div className="info-item">
                                        <label>COMPONENT</label>
                                        <span>{selectedTraceData.name}</span>
                                    </div>
                                    <div className="info-item">
                                        <label>AVAILABILITY</label>
                                        <span style={{ color: 'var(--success)' }}>LOCAL_VECTOR_CACHE</span>
                                    </div>
                                </div>
                                <div className="data-display">
                                    <div className="display-label">PAYLOAD_BUFFER:</div>
                                    <pre>{JSON.stringify(selectedTraceData.data || { status: 'No data emitted' }, null, 2)}</pre>
                                </div>
                            </div>
                        ) : (
                            <div className="screen-idle">
                                <p>WAITING FOR EXECUTION SIGNAL...</p>
                                <small>Run a query to begin real-time inspection</small>
                            </div>
                        )}
                    </div>
                </div>
            </main>

            <style jsx>{`
                .app-container {
                    max-width: 1200px !important;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                }
                .viz-container {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    padding: var(--space-4) var(--space-8) !important;
                }
                .pipeline-grid {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: var(--space-2);
                    margin: var(--space-4) 0;
                }
                .pipeline-row {
                    display: flex;
                    align-items: center;
                    gap: 0;
                }
                .pipeline-row.row-reverse {
                    flex-direction: row-reverse;
                }
                .pipeline-row-connector {
                    width: 100%;
                    max-width: 820px;
                    display: flex;
                    justify-content: flex-end;
                    padding-right: 70px; /* Aligns with middle of last step in Row 1 */
                }
                .connector-vertical {
                    width: 2px;
                    height: 20px;
                    background: var(--blue-800);
                    position: relative;
                }
                .connector-vertical::after {
                    content: '';
                    position: absolute;
                    bottom: -2px;
                    left: 50%;
                    transform: translateX(-50%);
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 6px solid var(--blue-800);
                }
                .viz-step-wrapper {
                    display: flex;
                    align-items: center;
                    flex-direction: inherit;
                }
                .viz-step {
                    width: 140px;
                    padding: var(--space-3);
                    background: var(--blue-900);
                    border: 1px solid var(--blue-800);
                    border-radius: var(--radius-lg);
                    cursor: pointer;
                    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                    text-align: center;
                    position: relative;
                }
                .viz-step:hover {
                    background: var(--blue-850);
                    transform: translateY(-2px);
                    border-color: var(--blue-700);
                }
                .viz-step-active {
                    background: var(--blue-800) !important;
                    border-color: var(--blue-400) !important;
                    box-shadow: 0 0 15px rgba(79, 127, 219, 0.15);
                }
                .viz-step-data {
                    border-bottom: 2px solid var(--blue-600);
                }
                .viz-step-number {
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 0.7rem;
                    font-weight: 800;
                    margin: 0 auto var(--space-1);
                    color: white;
                }
                .viz-step-title {
                    font-size: 0.7rem;
                    font-weight: 600;
                    color: var(--text-primary);
                    margin: 0;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                .viz-connector-h {
                    width: 30px;
                    height: 2px;
                    background: var(--blue-800);
                    position: relative;
                }
                .pipeline-row:not(.row-reverse) .viz-connector-h::after {
                    content: '';
                    position: absolute;
                    right: -2px;
                    top: 50%;
                    transform: translateY(-50%);
                    border-top: 4px solid transparent;
                    border-bottom: 4px solid transparent;
                    border-left: 6px solid var(--blue-800);
                }
                .pipeline-row.row-reverse .viz-connector-h::after {
                    content: '';
                    position: absolute;
                    left: -2px;
                    top: 50%;
                    transform: translateY(-50%);
                    border-top: 4px solid transparent;
                    border-bottom: 4px solid transparent;
                    border-right: 6px solid var(--blue-800);
                }
                .inspector-screen {
                    flex: 1;
                    min-height: 200px;
                    background: #02060c;
                    border: 1px solid #1e293b;
                    border-radius: var(--radius-lg);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    box-shadow: inset 0 0 50px rgba(0,0,0,0.5);
                }
                .screen-header {
                    background: #0f172a;
                    padding: var(--space-2) var(--space-4);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid #1e293b;
                }
                .screen-titling {
                    display: flex;
                    align-items: center;
                    gap: var(--space-2);
                }
                .screen-titling h3 {
                    font-size: 0.7rem;
                    font-family: var(--font-mono);
                    color: var(--blue-400);
                    margin: 0;
                    letter-spacing: 1px;
                }
                .screen-status {
                    font-size: 0.6rem;
                    font-family: var(--font-mono);
                    color: var(--success);
                    padding: 2px 8px;
                    background: rgba(16, 185, 129, 0.1);
                    border: 1px solid rgba(16, 185, 129, 0.2);
                    border-radius: 4px;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.6; }
                    100% { opacity: 1; }
                }
                .screen-content {
                    flex: 1;
                    padding: var(--space-4);
                    font-family: var(--font-mono);
                    overflow-y: auto;
                    color: #94a3b8;
                }
                .trace-info-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: var(--space-6);
                    margin-bottom: var(--space-6);
                    padding-bottom: var(--space-4);
                    border-bottom: 1px solid #1e293b;
                }
                .info-item label {
                    display: block;
                    font-size: 0.6rem;
                    text-transform: uppercase;
                    color: #64748b;
                    margin-bottom: 4px;
                }
                .info-item span {
                    font-size: 0.8rem;
                    color: #f1f5f9;
                    font-weight: 600;
                }
                .data-display pre {
                    background: #0a0f18;
                    padding: var(--space-4);
                    border-radius: var(--radius-md);
                    font-size: 0.75rem;
                    color: #38bdf8;
                    border: 1px solid #1e293b;
                    overflow-x: auto;
                    margin: 0;
                    line-height: 1.5;
                }
                .screen-idle, .screen-loading {
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                }
                .screen-idle p, .screen-loading p {
                    font-size: 0.8rem;
                    color: #64748b;
                    margin-bottom: 8px;
                }
                .screen-idle small {
                    font-size: 0.6rem;
                    color: #475569;
                }
                .scanner-line {
                    width: 100%;
                    height: 1px;
                    background: rgba(56, 189, 248, 0.5);
                    box-shadow: 0 0 10px #38bdf8;
                    position: absolute;
                    top: 0;
                    left: 0;
                    animation: scan 3s linear infinite;
                }
                @keyframes scan {
                    from { top: 0%; }
                    to { top: 100%; }
                }
            `}</style>
        </div>
    );
}
