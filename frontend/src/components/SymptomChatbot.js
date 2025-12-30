import React, { useState } from 'react';
import { MessageCircle, Send, X, Bot, User as UserIcon, AlertCircle, CheckCircle2, Activity } from 'lucide-react';
import Card from './ui/Card';
import Button from './ui/Button';

const API_URL = 'http://localhost:8000';

const SymptomChatbot = ({ user, onVitalsUpdate }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        {
            id: 1,
            type: 'bot',
            text: "Hello! I'm your health assistant. How are you feeling today? Describe any symptoms you're experiencing.",
            timestamp: new Date()
        }
    ]);
    const [inputText, setInputText] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    const handleSendMessage = async () => {
        if (!inputText.trim() || isAnalyzing) return;

        // Add user message
        const userMessage = {
            id: messages.length + 1,
            type: 'user',
            text: inputText,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, userMessage]);
        setInputText('');
        setIsAnalyzing(true);

        try {
            // Analyze symptoms
            const response = await fetch(`${API_URL}/symptoms/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.id,
                    symptoms: inputText
                })
            });

            if (response.ok) {
                const data = await response.json();

                // Add bot response
                const botMessage = {
                    id: messages.length + 2,
                    type: 'bot',
                    text: data.message,
                    severity: data.severity,
                    detectedSymptoms: data.detected_symptoms,
                    vitalChanges: data.suggested_vitals,
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, botMessage]);

                // Notify parent component about vital updates
                if (onVitalsUpdate) {
                    onVitalsUpdate();
                }
            } else {
                throw new Error('Failed to analyze symptoms');
            }
        } catch (error) {
            console.error('Error analyzing symptoms:', error);
            const errorMessage = {
                id: messages.length + 2,
                type: 'bot',
                text: "I'm sorry, I'm having trouble analyzing your symptoms right now. Please try again or contact your doctor directly if you're experiencing severe symptoms.",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'severe': return 'text-red-400 bg-red-500/10 border-red-500/20';
            case 'moderate': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
            default: return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
        }
    };

    const getSeverityIcon = (severity) => {
        switch (severity) {
            case 'severe': return AlertCircle;
            case 'moderate': return Activity;
            default: return CheckCircle2;
        }
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 z-50 p-4 bg-gradient-to-tr from-indigo-600 to-violet-600 text-white rounded-full shadow-2xl hover:shadow-indigo-500/50 hover:scale-110 transition-all duration-300 animate-pulse"
            >
                <MessageCircle size={28} />
            </button>
        );
    }

    return (
        <div className="fixed bottom-6 right-6 z-50 w-96 h-[600px] flex flex-col bg-gray-900 rounded-2xl shadow-2xl border border-gray-700 animate-slide-in">
            {/* Header */}
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-indigo-600 to-violet-600 rounded-t-2xl">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-white/20 rounded-lg">
                        <Bot size={24} className="text-white" />
                    </div>
                    <div>
                        <h3 className="font-bold text-white">Health Assistant</h3>
                        <p className="text-xs text-indigo-100">AI-Powered Symptom Checker</p>
                    </div>
                </div>
                <button
                    onClick={() => setIsOpen(false)}
                    className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                >
                    <X size={20} className="text-white" />
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-950/50">
                {messages.map(message => (
                    <div
                        key={message.id}
                        className={`flex gap-3 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                    >
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${message.type === 'bot' ? 'bg-indigo-600' : 'bg-gray-700'}`}>
                            {message.type === 'bot' ? <Bot size={18} className="text-white" /> : <UserIcon size={18} className="text-white" />}
                        </div>
                        <div className={`flex-1 ${message.type === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
                            <div className={`max-w-[85%] p-3 rounded-2xl ${message.type === 'bot' ? 'bg-gray-800 text-gray-200' : 'bg-indigo-600 text-white'}`}>
                                <p className="text-sm leading-relaxed">{message.text}</p>

                                {/* Show detected symptoms and vital changes for bot messages */}
                                {message.type === 'bot' && message.detectedSymptoms && (
                                    <div className="mt-3 pt-3 border-t border-gray-700">
                                        <p className="text-xs text-gray-400 mb-2">Detected Symptoms:</p>
                                        <div className="flex flex-wrap gap-1">
                                            {message.detectedSymptoms.map((symptom, idx) => (
                                                <span key={idx} className="px-2 py-1 bg-indigo-500/20 text-indigo-300 text-xs rounded-full">
                                                    {symptom.replace('_', ' ')}
                                                </span>
                                            ))}
                                        </div>

                                        {message.vitalChanges && Object.keys(message.vitalChanges).length > 0 && (
                                            <div className="mt-2">
                                                <p className="text-xs text-gray-400 mb-1">Vital Updates:</p>
                                                <div className="text-xs text-emerald-400">
                                                    {Object.entries(message.vitalChanges).map(([key, value]) => (
                                                        <div key={key}>• {key}: {value}</div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {message.severity && (
                                            <div className={`mt-2 px-2 py-1 rounded-md border text-xs font-semibold inline-flex items-center gap-1 ${getSeverityColor(message.severity)}`}>
                                                {React.createElement(getSeverityIcon(message.severity), { size: 12 })}
                                                {message.severity.toUpperCase()}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                            <span className="text-xs text-gray-500 mt-1 px-2">
                                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                    </div>
                ))}

                {isAnalyzing && (
                    <div className="flex gap-3">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
                            <Bot size={18} className="text-white" />
                        </div>
                        <div className="bg-gray-800 p-3 rounded-2xl">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Input */}
            <div className="p-4 bg-gray-900 border-t border-gray-800 rounded-b-2xl">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                        placeholder="Describe your symptoms..."
                        className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                        disabled={isAnalyzing}
                    />
                    <button
                        onClick={handleSendMessage}
                        disabled={!inputText.trim() || isAnalyzing}
                        className="p-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send size={20} />
                    </button>
                </div>
                <p className="text-xs text-gray-500 mt-2 text-center">
                    This is an AI assistant. For emergencies, call your doctor.
                </p>
            </div>
        </div>
    );
};

export default SymptomChatbot;
