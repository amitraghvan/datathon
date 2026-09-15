"use client";

import React, { useState, useRef, useEffect } from "react";
import { fetchApi } from "@/lib/api/client";
import type { AgentQueryResponse } from "@/lib/types";
import {
  Bot,
  Sparkles,
  Send,
  X,
  Minimize2,
  Maximize2,
  RotateCcw,
  Database,
  Cpu,
  Brain,
  ArrowUpRight,
} from "lucide-react";
import Link from "next/link";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  response?: AgentQueryResponse;
}

const QUICK_PROMPTS = [
  "Which district has the lowest attendance rate?",
  "Why is SCH0386 marked as high priority?",
  "Are attendance and FLN scores correlated?",
  "Are there Mid-Day Meal procurement outliers?",
  "What is the overall Data Trust Score?",
];

const THINKING_STEPS = [
  "Parsing intent with Semantic Graph...",
  "Compiling governed DuckDB SQL query...",
  "Executing evidence extraction...",
  "Synthesizing grounded executive narrative...",
  "Auditing citations against warehouse...",
];

export function GlobalAIChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [thinkingStep, setThinkingStep] = useState(0);
  const [sessionId, setSessionId] = useState<string>(() => `bot_${Math.random().toString(36).substring(2, 9)}`);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "**Hello! I am your EduPulse AI Decision Copilot.**\n\nI can analyze retention risk, triage high-priority schools, investigate procurement anomalies, and audit data quality across all 600 monitored institutions with 100% DuckDB-grounded provenance.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, messages, isLoading]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      interval = setInterval(() => {
        setThinkingStep((prev) => (prev + 1) % THINKING_STEPS.length);
      }, 700);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSend = async (textToSend?: string) => {
    const queryText = (textToSend || input).trim();
    if (!queryText || isLoading) return;

    const userMsg: ChatMessage = {
      id: `usr_${Date.now()}`,
      role: "user",
      content: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);
    setThinkingStep(0);

    try {
      const res = await fetchApi<AgentQueryResponse>(
        "/agent/query",
        {},
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: queryText,
            session_id: sessionId,
            active_filters: {},
          }),
        }
      );

      const assistantMsg: ChatMessage = {
        id: res.query_id || `bot_${Date.now()}`,
        role: "assistant",
        content: res.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        response: res,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        role: "assistant",
        content:
          "⚠️ **Connection Notice:** Unable to reach the EduPulse Decision Intelligence engine. Please verify the backend service is running on `http://localhost:8000/api/v1`.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSessionId(`bot_${Math.random().toString(36).substring(2, 9)}`);
    setMessages([
      {
        id: "welcome_reset",
        role: "assistant",
        content:
          "Conversation memory reset. Ask any educational welfare question to begin a new analytical session.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  };

  return (
    <div aria-label="EduPulse AI Floating Copilot" className="fixed bottom-5 right-5 z-50 flex flex-col items-end pointer-events-none">
      {/* ── CHAT WINDOW CONTAINER ─────────────────────────────────── */}
      {isOpen && (
        <div
          className={`pointer-events-auto mb-3 flex flex-col rounded-2xl bg-[#0F172A]/95 border border-[#38BDF8]/30 shadow-2xl shadow-[#0284C7]/25 backdrop-blur-2xl transition-all duration-300 overflow-hidden ${
            isExpanded
              ? "w-[92vw] sm:w-[620px] h-[82vh] max-h-[800px]"
              : "w-[92vw] sm:w-[430px] h-[72vh] max-h-[620px]"
          }`}
        >
          {/* Glassmorphic Header */}
          <div className="bg-gradient-to-r from-[#1E293B] via-[#0F172A] to-[#1E293B] border-b border-[#2A364F] px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-[#0284C7] to-[#6366F1] text-white shadow-md shadow-[#0284C7]/30">
                <Sparkles className="w-4 h-4 animate-pulse" />
                <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[#10B981] ring-2 ring-[#0F172A]" />
              </div>
              <div>
                <div className="text-xs font-bold text-white flex items-center gap-1.5 tracking-wide">
                  EduPulse AI Copilot
                  <span className="text-[9px] font-mono font-semibold uppercase px-1.5 py-0.2 rounded bg-[#0284C7]/20 text-[#38BDF8] border border-[#0284C7]/30">
                    Phase 6
                  </span>
                </div>
                <div className="text-[10px] text-[#94A3B8] flex items-center gap-1.5">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-[#10B981]" />
                  DuckDB Verified (94.6% Trust)
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1 text-[#94A3B8]">
              <button
                onClick={handleReset}
                title="Reset session memory"
                className="p-1.5 hover:text-white hover:bg-[#1E293B] rounded-md transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                title={isExpanded ? "Collapse" : "Expand"}
                className="p-1.5 hover:text-white hover:bg-[#1E293B] rounded-md transition-colors hidden sm:block"
              >
                {isExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                title="Close chat"
                className="p-1.5 hover:text-white hover:bg-[#1E293B] rounded-md transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Chat Messages Body */}
          <div className="flex-1 p-3.5 space-y-3.5 overflow-y-auto bg-gradient-to-b from-[#0B0F19]/90 to-[#0F172A]/90">
            {messages.map((m) => {
              const isUser = m.role === "user";
              return (
                <div key={m.id} className={`flex gap-2.5 ${isUser ? "justify-end" : "justify-start"}`}>
                  {!isUser && (
                    <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#0284C7] to-[#3B82F6] flex items-center justify-center text-white shrink-0 mt-0.5 shadow-sm">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div className={`max-w-[85%] space-y-2 ${isUser ? "items-end" : "items-start"}`}>
                    <div
                      className={`p-3 rounded-2xl text-xs leading-relaxed shadow-md ${
                        isUser
                          ? "bg-gradient-to-r from-[#0284C7] to-[#0369A1] text-white rounded-br-sm"
                          : "bg-[#151D2E] text-[#E2E8F0] border border-[#2A364F] rounded-bl-sm"
                      }`}
                    >
                      {/* Assistant Metadata Badges */}
                      {!isUser && m.response && (
                        <div className="flex flex-wrap items-center gap-1.5 mb-2 pb-1.5 border-b border-[#2A364F]/60">
                          <span className="text-[9px] font-mono font-bold uppercase px-1.5 py-0.5 rounded bg-[#8B5CF6]/20 text-[#A78BFA] border border-[#8B5CF6]/30 flex items-center gap-1">
                            {m.response.reasoning_mode === "llama_3.1" ? (
                              <><Brain className="w-2.5 h-2.5" /> Llama 3.1</>
                            ) : (
                              <><Cpu className="w-2.5 h-2.5" /> Governed SQL</>
                            )}
                          </span>
                          <span className="text-[9px] font-mono font-bold uppercase px-1.5 py-0.5 rounded bg-[#0284C7]/20 text-[#38BDF8]">
                            {m.response.intent_type}
                          </span>
                          <span className="text-[9px] font-mono text-[#64748B]">
                            {m.response.timings_ms?.total_duration_ms || 0}ms
                          </span>
                        </div>
                      )}

                      <div className="whitespace-pre-line font-sans">{m.content}</div>

                      {/* Quick Citation Reference Pill */}
                      {!isUser && m.response && m.response.citations && m.response.citations.length > 0 && (
                        <div className="mt-2.5 pt-2 border-t border-[#2A364F]/60 flex items-center justify-between text-[10px] text-[#94A3B8]">
                          <span className="flex items-center gap-1 text-[#38BDF8]">
                            <Database className="w-3 h-3" />
                            {m.response.citations.length} Verified Citations
                          </span>
                          <span className="font-mono text-[#64748B]">
                            N = {m.response.evidence_count} rows
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="text-[9px] text-[#64748B] px-1 font-mono">
                      {m.timestamp}
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Thinking / Stepper Indicator */}
            {isLoading && (
              <div className="flex gap-2.5 justify-start items-start animate-in fade-in duration-200">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#8B5CF6] to-[#6366F1] flex items-center justify-center text-white shrink-0 mt-0.5 animate-pulse">
                  <Cpu className="w-4 h-4" />
                </div>
                <div className="bg-[#151D2E] border border-[#38BDF8]/40 rounded-2xl rounded-bl-sm p-3 text-xs text-[#94A3B8] shadow-lg max-w-[85%] space-y-2">
                  <div className="flex items-center gap-2 text-white font-medium text-[11px]">
                    <span className="w-2 h-2 rounded-full bg-[#38BDF8] animate-ping" />
                    {THINKING_STEPS[thinkingStep]}
                  </div>
                  <div className="w-full bg-[#0B0F19] rounded-full h-1 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-[#0284C7] to-[#8B5CF6] h-full transition-all duration-300"
                      style={{ width: `${((thinkingStep + 1) / THINKING_STEPS.length) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Demo Prompts Carousel */}
          <div className="px-3 py-1.5 bg-[#0B0F19]/80 border-t border-[#2A364F] flex items-center gap-1.5 overflow-x-auto no-scrollbar">
            <span className="text-[10px] text-[#64748B] font-semibold uppercase shrink-0">Try:</span>
            {QUICK_PROMPTS.map((p, i) => (
              <button
                key={i}
                onClick={() => handleSend(p)}
                disabled={isLoading}
                className="text-[10px] text-[#94A3B8] hover:text-white bg-[#151D2E] hover:bg-[#1E293B] border border-[#2A364F] hover:border-[#38BDF8]/40 px-2 py-0.5 rounded-full shrink-0 transition-colors truncate max-w-[220px]"
              >
                {p}
              </button>
            ))}
          </div>

          {/* Chat Input Field */}
          <div className="p-3 bg-[#0F172A] border-t border-[#2A364F]">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="relative flex items-center"
            >
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about school risk, attendance, or procurement..."
                disabled={isLoading}
                className="w-full bg-[#0B0F19] border border-[#2A364F] focus:border-[#0284C7] rounded-xl pl-3.5 pr-10 py-2.5 text-xs text-white placeholder-[#64748B] focus:outline-none transition-colors shadow-inner"
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="absolute right-1.5 p-1.5 bg-[#0284C7] hover:bg-[#0369A1] disabled:opacity-40 disabled:hover:bg-[#0284C7] text-white rounded-lg transition-colors shadow-sm"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>

            <div className="flex items-center justify-between text-[9px] text-[#64748B] mt-2 px-1">
              <span>Zero-hallucination DuckDB compilation</span>
              <Link
                href="/ai-analyst"
                className="text-[#38BDF8] hover:underline flex items-center gap-0.5 font-medium"
              >
                Full Workbench <ArrowUpRight className="w-2.5 h-2.5" />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* ── FLOATING LAUNCH TRIGGER BUTTON ────────────────────────── */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle AI Decision Assistant"
        className="pointer-events-auto group relative flex items-center gap-2.5 px-3.5 py-2.5 rounded-full bg-gradient-to-r from-[#0284C7] via-[#4F46E5] to-[#7C3AED] hover:from-[#0369A1] hover:to-[#6D28D9] text-white font-medium shadow-xl shadow-[#0284C7]/30 hover:shadow-[#0284C7]/50 transition-all duration-300 hover:scale-105 active:scale-95 border border-white/20"
      >
        {/* Pulsing Aura */}
        <span className="absolute -inset-0.5 rounded-full bg-gradient-to-r from-[#38BDF8] to-[#818CF8] opacity-50 blur-sm group-hover:opacity-75 animate-pulse transition duration-300 -z-10" />

        <div className="relative flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
          <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-[#10B981] ring-2 ring-[#0F172A] animate-ping" />
        </div>

        <div className="flex flex-col text-left">
          <span className="text-xs font-bold tracking-wide flex items-center gap-1">
            EduPulse AI
            <Sparkles className="w-3 h-3 text-[#FDE047]" />
          </span>
          <span className="text-[10px] text-white/80 font-mono -mt-0.5">
            Ask Copilot
          </span>
        </div>
      </button>
    </div>
  );
}
