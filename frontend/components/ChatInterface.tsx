'use client';

import { useState } from 'react';

interface Source {
    title: string;
    page: number;
    text: string;
}

interface Message {
    role: 'user' | 'assistant';
    content: string;
    sources?: Source[];
}

export default function ChatInterface() {
    const [query, setQuery] = useState('');
    const [history, setHistory] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);

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
                sources: data.sources
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
        <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
            <header className="py-4 border-b border-gray-200 mb-4">
                <h1 className="text-2xl font-bold text-gray-800">Sema-Data</h1>
                <p className="text-sm text-gray-500">AI-Driven Transparency for African Public Records</p>
            </header>

            <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                {history.length === 0 && (
                    <div className="text-center text-gray-400 mt-20">
                        <p>Ask a question about public records...</p>
                        <p className="text-xs mt-2">Try: "What is the healthcare budget for Kisumu?"</p>
                    </div>
                )}

                {history.map((msg, idx) => (
                    <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                        <div className={`max-w-[80%] p-3 rounded-lg ${msg.role === 'user'
                                ? 'bg-blue-600 text-white rounded-br-none'
                                : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none shadow-sm'
                            }`}>
                            <p>{msg.content}</p>
                        </div>

                        {msg.sources && msg.sources.length > 0 && (
                            <div className="mt-2 text-xs text-gray-500 ml-2">
                                <p className="font-semibold mb-1">Sources:</p>
                                <div className="flex gap-2 flex-wrap">
                                    {msg.sources.map((src, i) => (
                                        <span key={i} className="bg-gray-200 px-2 py-1 rounded text-gray-700">
                                            {src.title} (p. {src.page})
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                ))}

                {loading && (
                    <div className="flex items-center space-x-2 text-gray-400">
                        <div className="animate-pulse">Thinking...</div>
                    </div>
                )}
            </div>

            <form onSubmit={handleSearch} className="flex gap-2">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a question..."
                    className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loading}
                />
                <button
                    type="submit"
                    className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    disabled={loading}
                >
                    Send
                </button>
            </form>
        </div>
    );
}
