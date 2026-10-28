'use client';

import React, { useState } from 'react';
import { 
  X, 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  Database, 
  Scale, 
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import { DatasetInfo } from '@/types';
import { ShimmerBadge } from '@/components/ui/shimmer-badge';

interface AICopilotDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  dataset: DatasetInfo;
}

interface Message {
  id: string;
  sender: 'ai' | 'user';
  text: string;
  citation?: string;
}

export function AICopilotDrawer({ isOpen, onClose, dataset }: AICopilotDrawerProps) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      text: `Hello! I'm your Neurolytix AI Data Agent. I've indexed **${dataset.name}** (${dataset.rows.toLocaleString()} rows). What questions or decisions would you like help with today?`,
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);

  if (!isOpen) return null;

  const handleSend = (textToSend?: string) => {
    const q = textToSend || input;
    if (!q.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: q,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    setTimeout(() => {
      let aiResponseText = `Based on our analysis of **${dataset.name}**, `;
      let citation = '';

      if (q.toLowerCase().includes('churn') || q.toLowerCase().includes('leave')) {
        aiResponseText += `customers who log more than 3 support tickets have an 81.4% churn probability compared to 8.2% baseline. Focusing on resolving support tickets within 24 hours will have the highest immediate impact on retention.`;
        citation = `Ground Truth: 4,820 rows • Feature weight: 38%`;
      } else if (q.toLowerCase().includes('model') || q.toLowerCase().includes('accuracy')) {
        aiResponseText += `the highest performing model is **NeuroCatBoost v4.2** with a 94.8% ROC-AUC score, trained across 5-fold cross validation. It outperforms LightGBM (93.4%) and XGBoost (92.7%).`;
        citation = `Evaluation: 5-Fold CV • LogLoss: 0.182`;
      } else {
        aiResponseText += `the dataset shows 9 features with an overall health score of 94%. We detected 16 outlier records primarily concentrated in extreme monthly spends.`;
        citation = `Data Quality Scan: 0 missing values remain`;
      }

      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: aiResponseText,
          citation,
        },
      ]);
      setIsTyping(false);
    }, 800);
  };

  const suggestions = [
    "What is the top driver of customer churn?",
    "Which model has the highest prediction accuracy?",
    "Are there any outliers in monthly spend?",
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white shadow-2xl flex flex-col border-l border-slate-200">
          {/* Header */}
          <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/80">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-indigo-600 text-white shadow-sm">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <h3 className="text-sm font-bold text-slate-900 font-outfit">AI Data Agent</h3>
                  <ShimmerBadge variant="indigo" className="text-[9px] py-0">
                    Offline RAG
                  </ShimmerBadge>
                </div>
                <p className="text-[11px] text-slate-500">Dataset-aware conversational assistant</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Active Dataset Context Badge */}
          <div className="px-4 py-2 bg-indigo-50/50 border-b border-indigo-100 flex items-center justify-between text-xs text-indigo-900">
            <div className="flex items-center gap-1.5 truncate">
              <Database className="h-3.5 w-3.5 text-indigo-600" />
              <span className="truncate font-semibold">{dataset.name}</span>
            </div>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-100">
              {dataset.rows.toLocaleString()} rows
            </span>
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m) => {
              const isAi = m.sender === 'ai';
              return (
                <div
                  key={m.id}
                  className={`flex items-start gap-2.5 ${isAi ? '' : 'flex-row-reverse'}`}
                >
                  <div
                    className={`flex-shrink-0 h-7 w-7 rounded-lg flex items-center justify-center text-xs ${
                      isAi
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'bg-slate-800 text-white'
                    }`}
                  >
                    {isAi ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                  </div>
                  <div
                    className={`max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed ${
                      isAi
                        ? 'bg-slate-100 text-slate-800 border border-slate-200/80 rounded-tl-sm'
                        : 'bg-indigo-600 text-white rounded-tr-sm shadow-sm'
                    }`}
                  >
                    <p>{m.text}</p>
                    {m.citation && (
                      <div className="mt-2 pt-1.5 border-t border-slate-200/60 flex items-center gap-1 text-[10px] text-slate-500">
                        <ShieldCheck className="h-3 w-3 text-emerald-600" />
                        <span>{m.citation}</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {isTyping && (
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Bot className="h-4 w-4 animate-spin text-indigo-500" />
                <span>AI Data Agent is reasoning over dataset...</span>
              </div>
            )}
          </div>

          {/* Suggestions Strip */}
          <div className="p-3 bg-slate-50 border-t border-slate-100 space-y-1.5">
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
              Quick Inquiries:
            </p>
            <div className="flex flex-col gap-1">
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(s)}
                  className="text-left text-xs text-indigo-700 hover:text-indigo-900 hover:bg-indigo-50/60 p-1.5 rounded transition truncate"
                >
                  → {s}
                </button>
              ))}
            </div>
          </div>

          {/* Input Box */}
          <div className="p-3 border-t border-slate-200 bg-white">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about trends, predictions, or anomalies..."
                className="flex-1 px-3 py-2 rounded-xl border border-slate-300 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="submit"
                className="p-2 rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 transition cursor-pointer shadow-sm"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
