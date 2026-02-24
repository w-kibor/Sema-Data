'use client';

import { useMemo, useState } from 'react';

interface Source {
    title: string;
    page: number;
    text: string;
    url?: string;
    thumbnailUrl?: string;
    agency?: string;
    publishDate?: string;
    fileSize?: string;
}

interface Message {
    role: 'user' | 'assistant';
    content: string;
    sources?: Source[];
}

const quickQueries = [
    'Analyze Nairobi County Budget 2024',
    'Summarize recent road procurement tenders',
    'List education grants in Nakuru',
    'Show new housing levy regulations',
];

const trendingTopics = [
    'Trending: New Housing Levy Regulations',
    'Trending: Coastline Port Expansion 2025',
    'Trending: County Hospital Funding Gaps',
];

const stats = [
    { label: 'Documents Indexed', value: '1.8M' },
    { label: 'Active Queries', value: '14,280' },
    { label: 'Latest Uploads', value: 'Gazette Vol. CXXVI' },
];

const savedInvestigations = [
    'Kisumu Health Budget Audit',
    'Mombasa Road Tender Review',
    'Nairobi Housing Levy Tracker',
];

const dataCategories = ['Legal', 'Finance', 'Infrastructure', 'Education', 'Procurement'];

export default function ChatInterface() {
    const [query, setQuery] = useState('');
    const [history, setHistory] = useState<Message[]>([
        {
            role: 'assistant',
            content:
                'Welcome to Sema-Data. Ask about budgets, tenders, or gazettes. I will cite sources so you can verify every claim.',
            sources: [
                {
                    title: 'Kenya Gazette Vol. CXXVI',
                    page: 18,
                    text: 'Sample reference snippet for transparency.',
                    url: 'http://localhost:8000/pdfs/kenya-gazette-vol-cxxvi.pdf',
                    thumbnailUrl: 'http://localhost:8000/thumbnails/kenya-gazette-vol-cxxvi.png',
                    agency: 'Kenya Gazette Office',
                    publishDate: '2024-01-18',
                    fileSize: '3.2 MB',
                },
            ],
        },
    ]);
    const [loading, setLoading] = useState(false);

    const budgetBreakdown = useMemo(
        () => [
            { label: 'Healthcare', value: 42 },
            { label: 'Infrastructure', value: 28 },
            { label: 'Education', value: 18 },
            { label: 'Water & Sanitation', value: 12 },
        ],
        []
    );

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        const userMsg: Message = { role: 'user', content: query };
        setHistory(prev => [...prev, userMsg]);
        setLoading(true);
        setQuery('');

        try {
            const res = await fetch('http://localhost:8000/api/v1/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: userMsg.content, history: [] }),
            });

            const data = await res.json();
            const aiMsg: Message = {
                role: 'assistant',
                content: data.answer,
                sources: data.sources,
            };
            setHistory(prev => [...prev, aiMsg]);
        } catch (err) {
            console.error('Error fetching chat response:', err);
            setHistory(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app-shell min-h-screen text-slate-100">
            <header className="px-6 pt-8 pb-6 md:px-10">
                <div className="mx-auto flex max-w-6xl items-center justify-between">
                    <div>
                        <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Sema-Data</p>
                        <h1 className="mt-2 text-3xl font-semibold text-white md:text-4xl">AI-Driven Transparency for African Public Records</h1>
                        <p className="mt-2 max-w-2xl text-sm text-slate-200/80">
                            Search gazettes, budgets, and procurement data with verified sources and real-time transparency signals.
                        </p>
                    </div>
                    <div className="hidden items-center gap-3 md:flex">
                        <span className="text-xs text-slate-200/70">Secure • Open • Verifiable</span>
                        <button className="rounded-full bg-emerald-400 px-4 py-2 text-xs font-semibold text-slate-900">Request Access</button>
                    </div>
                </div>
            </header>

            <section className="px-6 md:px-10">
                <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[1.3fr_0.7fr]">
                    <div className="glass-card rounded-3xl p-6 md:p-8">
                        <div className="flex flex-col gap-6">
                            <div>
                                <p className="text-sm text-emerald-200">Conversational Search</p>
                                <h2 className="mt-2 text-2xl font-semibold text-white">Ask anything, verify everything.</h2>
                            </div>
                            <form onSubmit={handleSearch} className="flex flex-col gap-3 md:flex-row">
                                <div className="flex flex-1 items-center gap-3 rounded-full bg-white/90 px-5 py-3 text-slate-800 shadow-lg">
                                    <span className="text-emerald-500">●</span>
                                    <input
                                        type="text"
                                        value={query}
                                        onChange={(e) => setQuery(e.target.value)}
                                        placeholder="Ask a transparency question"
                                        className="flex-1 bg-transparent text-sm outline-none"
                                        disabled={loading}
                                    />
                                    <span className="rounded-full bg-slate-900/10 px-2 py-1 text-[10px] uppercase tracking-[0.2em] text-slate-600">Live</span>
                                </div>
                                <button
                                    type="submit"
                                    className="rounded-full bg-emerald-400 px-6 py-3 text-sm font-semibold text-slate-900 hover:bg-emerald-300 disabled:opacity-60"
                                    disabled={loading}
                                >
                                    Ask Sema
                                </button>
                            </form>

                            <div className="flex flex-wrap gap-2">
                                {quickQueries.map((item) => (
                                    <button
                                        key={item}
                                        type="button"
                                        onClick={() => setQuery(item)}
                                        className="rounded-full border border-emerald-200/40 bg-emerald-200/10 px-3 py-1 text-xs text-emerald-100 hover:bg-emerald-200/20"
                                    >
                                        {item}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="glass-card rounded-3xl p-6">
                        <h3 className="text-sm font-semibold text-white">Transparency Pulse</h3>
                        <div className="mt-4 grid gap-3">
                            {stats.map((stat) => (
                                <div key={stat.label} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                                    <p className="text-xs uppercase tracking-[0.25em] text-slate-300/70">{stat.label}</p>
                                    <p className="mt-2 text-lg font-semibold text-emerald-200">{stat.value}</p>
                                </div>
                            ))}
                        </div>
                        <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
                            <p className="text-xs uppercase tracking-[0.25em] text-slate-300/70">Trending Topics</p>
                            <ul className="mt-3 space-y-2 text-sm text-slate-200/90">
                                {trendingTopics.map((topic) => (
                                    <li key={topic} className="flex items-center gap-2">
                                        <span className="h-2 w-2 rounded-full bg-emerald-300" />
                                        {topic}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            <section className="px-6 pb-24 pt-8 md:px-10">
                <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[0.35fr_1fr]">
                    <aside className="glass-card hidden h-full rounded-3xl p-6 lg:block">
                        <div className="space-y-6">
                            <div>
                                <p className="text-xs uppercase tracking-[0.3em] text-emerald-200">Saved Investigations</p>
                                <ul className="mt-3 space-y-3 text-sm text-slate-200/90">
                                    {savedInvestigations.map((item) => (
                                        <li key={item} className="rounded-xl border border-white/10 bg-white/5 px-3 py-2">
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div>
                                <p className="text-xs uppercase tracking-[0.3em] text-emerald-200">Data Categories</p>
                                <div className="mt-3 flex flex-wrap gap-2">
                                    {dataCategories.map((item) => (
                                        <span key={item} className="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs text-white/80">
                                            {item}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </aside>

                    <div className="glass-card rounded-3xl p-6 md:p-8">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-emerald-200">Sema-Data Assistant</p>
                                <h3 className="text-2xl font-semibold text-white">Investigative Chat</h3>
                            </div>
                            <div className="hidden items-center gap-2 rounded-full border border-emerald-200/40 bg-emerald-200/10 px-3 py-2 text-xs text-emerald-100 md:flex">
                                <span className="h-2 w-2 rounded-full bg-emerald-300 pulse-ring" />
                                Live data feed
                            </div>
                        </div>

                        <div className="mt-6 space-y-5">
                            {history.map((msg, idx) => (
                                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div
                                        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                                            msg.role === 'user'
                                                ? 'bg-emerald-400 text-slate-900 shadow-lg'
                                                : 'bg-white/10 text-slate-100'
                                        }`}
                                    >
                                        <p>{msg.content}</p>
                                        {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                                            <div className="mt-4 space-y-3">
                                                <div className="flex flex-wrap gap-2">
                                                    {msg.sources.map((src, i) => (
                                                        <a
                                                            key={`${src.title}-${i}`}
                                                            href={src.url ?? '#'}
                                                            target={src.url ? '_blank' : undefined}
                                                            rel={src.url ? 'noreferrer' : undefined}
                                                            className="group relative rounded-full border border-emerald-200/40 bg-emerald-200/10 px-3 py-1 text-[11px] text-emerald-100"
                                                        >
                                                            {src.title} p.{src.page}
                                                            <span className="pointer-events-none absolute -top-2 left-1/2 hidden w-56 -translate-x-1/2 -translate-y-full rounded-xl border border-white/20 bg-slate-900/90 p-3 text-[11px] text-white/90 shadow-lg group-hover:block">
                                                                <span className="block text-emerald-200">Source Details</span>
                                                                <span className="mt-1 block">Agency: {src.agency ?? 'Unknown'}</span>
                                                                <span className="block">Published: {src.publishDate ?? 'N/A'}</span>
                                                                <span className="block">File size: {src.fileSize ?? 'N/A'}</span>
                                                            </span>
                                                        </a>
                                                    ))}
                                                </div>
                                                <div className="grid gap-3 md:grid-cols-[120px_1fr]">
                                                    <div className="rounded-xl border border-white/20 bg-gradient-to-br from-emerald-300/20 to-white/10 p-3">
                                                        {msg.sources[0].thumbnailUrl ? (
                                                            <img
                                                                src={msg.sources[0].thumbnailUrl}
                                                                alt={`${msg.sources[0].title} preview`}
                                                                className="h-full w-full rounded-lg object-cover"
                                                            />
                                                        ) : (
                                                            <div className="flex h-full flex-col items-center justify-center text-xs text-emerald-100">
                                                                <span className="text-lg font-semibold">PDF</span>
                                                                <span>Preview</span>
                                                            </div>
                                                        )}
                                                    </div>
                                                    <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-xs text-slate-200/80">
                                                        {msg.sources[0].text}
                                                    </div>
                                                </div>
                                                {msg.content.toLowerCase().includes('budget') && (
                                                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                                                        <p className="text-xs uppercase tracking-[0.3em] text-emerald-200">Budget Breakdown</p>
                                                        <div className="mt-4 space-y-3">
                                                            {budgetBreakdown.map((item) => (
                                                                <div key={item.label} className="flex items-center gap-3">
                                                                    <span className="w-28 text-xs text-slate-200/80">{item.label}</span>
                                                                    <div className="h-2 flex-1 rounded-full bg-white/10">
                                                                        <div
                                                                            className="h-2 rounded-full bg-emerald-300"
                                                                            style={{ width: `${item.value}%` }}
                                                                        />
                                                                    </div>
                                                                    <span className="text-xs text-slate-200/60">{item.value}%</span>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}

                            {loading && (
                                <div className="flex items-center gap-2 text-sm text-emerald-200/80">
                                    <span className="h-2 w-2 rounded-full bg-emerald-300 animate-pulse" />
                                    Sema is reading the documents...
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </section>

            <nav className="fixed bottom-4 left-1/2 z-20 flex w-[92%] -translate-x-1/2 items-center justify-between rounded-full bg-white/10 px-6 py-3 text-xs text-white/90 shadow-lg backdrop-blur md:hidden">
                <button className="flex flex-col items-center gap-1">
                    <span className="h-2 w-2 rounded-full bg-emerald-300" />
                    Assistant
                </button>
                <button className="flex flex-col items-center gap-1">
                    <span className="h-2 w-2 rounded-full bg-white/60" />
                    Documents
                </button>
                <button className="flex flex-col items-center gap-1">
                    <span className="h-2 w-2 rounded-full bg-white/60" />
                    Saved
                </button>
            </nav>
        </div>
    );
}
