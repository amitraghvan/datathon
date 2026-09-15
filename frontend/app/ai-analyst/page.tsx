"use client";

import React, { useState } from "react";
import { Header } from "@/components/layout/header";
import { fetchApi } from "@/lib/api/client";
import type { AgentQueryResponse } from "@/lib/types";
import {
  Sparkles,
  Send,
  ShieldAlert,
  Database,
  CheckCircle,
  FileCheck2,
  BarChart3,
  RotateCcw,
  Clock,
  ThumbsUp,
  ThumbsDown,
  ChevronRight,
  AlertTriangle,
  Layers,
  TrendingUp,
  Target,
  FileText,
  Cpu,
  Zap,
  Brain,
  Shield,
  Search,
  Activity,
  PieChart,
  Building,
  ShieldCheck,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ScatterChart,
  Scatter,
} from "recharts";

interface ShowcaseMission {
  category: string;
  icon: any;
  title: string;
  description: string;
  prompt: string;
  tag: string;
  color: string;
}

const SHOWCASE_MISSIONS: ShowcaseMission[] = [
  {
    category: "District Benchmarking",
    icon: BarChart3,
    title: "Regional Attendance & Academic Disparity",
    description: "Compare average attendance against FLN scores across all 23 districts to identify lagging blocks.",
    prompt: "Which district has the lowest attendance rate?",
    tag: "Benchmark",
    color: "#0284C7",
  },
  {
    category: "Critical Triage",
    icon: Target,
    title: "High Priority School Root-Cause Diagnosis",
    description: "Unpack infrastructure deficits, attendance lag, and risk drivers for critical priority institutions.",
    prompt: "Why is SCH0386 marked as high priority?",
    tag: "Diagnostic",
    color: "#EF4444",
  },
  {
    category: "Statistical Association",
    icon: TrendingUp,
    title: "Daily Attendance vs. FLN Score Correlation",
    description: "Verify non-causal bivariate Pearson (r = 0.453) and Spearman correlation across 600 institutions.",
    prompt: "Does student attendance correlate with FLN academic scores?",
    tag: "Non-Causal",
    color: "#10B981",
  },
  {
    category: "Procurement & Welfare",
    icon: PieChart,
    title: "Mid-Day Meal Spend Outlier Detection",
    description: "Audit commodity cost variance ratios and flag peer group benchmark exceptions without accusations.",
    prompt: "Are there any Mid-Day Meal procurement cost outliers?",
    tag: "Nutrition",
    color: "#F59E0B",
  },
  {
    category: "Infrastructure Impact",
    icon: Building,
    title: "Amenity Deficits & Learning Efficacy",
    description: "Evaluate observational score differences for schools with complete electricity vs. unverified status.",
    prompt: "How do schools with electricity compare on academic performance?",
    tag: "Amenities",
    color: "#8B5CF6",
  },
  {
    category: "Data Trust & Governance",
    icon: ShieldCheck,
    title: "Warehouse Quality Gates & Quarantine Audit",
    description: "Audit the 10 automated data quality gates, 37,974 trusted rows, and 1,929 quarantined anomaly records.",
    prompt: "What is the data trust score and profile completeness across schools?",
    tag: "Governance",
    color: "#06B6D4",
  },
];

const PIPELINE_STEPS = [
  { label: "Semantic Graph Parsing", icon: Brain, color: "#8B5CF6", detail: "Resolving intent & canonical entities" },
  { label: "Governed SQL Compilation", icon: Search, color: "#0284C7", detail: "Read-only DuckDB view query" },
  { label: "DuckDB Warehouse Execution", icon: Database, color: "#10B981", detail: "Retrieving canonical evidence records" },
  { label: "Llama 3.1 Answer Synthesis", icon: Cpu, color: "#F59E0B", detail: "Formulating grounded executive findings" },
  { label: "Claim & Causal Audit", icon: Shield, color: "#10B981", detail: "Anti-hallucination verification" },
];

export default function AIAnalystPage() {
  const [query, setQuery] = useState("");
  const [sessionId, setSessionId] = useState<string>(() => `sess_${Math.random().toString(36).substring(2, 9)}`);
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<AgentQueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"analysis" | "visuals" | "actions" | "evidence">("analysis");
  const [feedbackGiven, setFeedbackGiven] = useState<Record<string, boolean>>({});
  const [pipelineStep, setPipelineStep] = useState(0);

  const handleSubmit = async (q: string) => {
    if (!q.trim()) return;
    setIsLoading(true);
    setError(null);
    setPipelineStep(0);

    // Animate pipeline progression
    const stepTimers = PIPELINE_STEPS.map((_, i) =>
      setTimeout(() => setPipelineStep(i), i * 500)
    );

    try {
      const res = await fetchApi<AgentQueryResponse>("/agent/query", {}, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: q,
          session_id: sessionId,
          active_filters: {},
        }),
      });
      setResponse(res);
      setActiveTab("analysis");
    } catch (err: any) {
      setError(err?.message || "Failed to communicate with Decision Intelligence Agent.");
    } finally {
      stepTimers.forEach(clearTimeout);
      setIsLoading(false);
    }
  };

  const handleFeedback = async (helpful: boolean) => {
    if (!response) return;
    try {
      await fetchApi("/agent/feedback", {}, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query_id: response.query_id,
          helpful,
          comments: helpful ? "Verified accurate reasoning" : "Flagged for manual review",
          session_id: sessionId,
        }),
      });
      setFeedbackGiven((prev) => ({ ...prev, [response.query_id]: helpful }));
    } catch (err) {
      console.error("Feedback error:", err);
    }
  };

  const handleResetSession = () => {
    setSessionId(`sess_${Math.random().toString(36).substring(2, 9)}`);
    setResponse(null);
    setQuery("");
    setError(null);
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#0B0F19]">
      <Header
        title="AI Analyst — Decision Intelligence Workbench"
        subtitle="Autonomous Graph-First reasoning agent grounded strictly in canonical DuckDB warehouse views with zero-hallucination provenance."
      />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* ── TOP HERO BANNER & LIVE SYSTEM STATUS ───────────────────── */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0F172A] via-[#1E293B] to-[#0F172A] border border-[#38BDF8]/20 p-6 shadow-2xl shadow-[#0284C7]/10">
          <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-[#0284C7]/10 via-[#6366F1]/10 to-transparent rounded-full blur-3xl pointer-events-none" />
          
          <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold tracking-wider uppercase bg-[#0284C7]/20 text-[#38BDF8] border border-[#0284C7]/40 shadow-sm">
                  <Sparkles className="w-3 h-3 animate-spin text-[#38BDF8]" style={{ animationDuration: "6s" }} />
                  Phase 6 Graph-First Decision Intelligence Core
                </span>
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-mono text-[#10B981] bg-[#10B981]/15 border border-[#10B981]/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
                  Live Grounded
                </span>
              </div>
              <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
                Enterprise Autonomous Education Analyst
              </h1>
              <p className="text-xs sm:text-sm text-[#94A3B8] max-w-2xl leading-relaxed">
                Query school triage queues, examine peer benchmark anomalies, and audit retention drivers with guaranteed zero-hallucination execution over canonical DuckDB data.
              </p>
            </div>

            {/* Quick Status Chips Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 shrink-0">
              <div className="bg-[#0B0F19]/80 border border-[#2A364F] rounded-xl p-2.5 space-y-1">
                <div className="text-[10px] uppercase font-bold text-[#64748B]">Reasoning Model</div>
                <div className="text-xs font-bold text-white flex items-center gap-1">
                  <Brain className="w-3.5 h-3.5 text-[#8B5CF6]" />
                  Llama 3.1
                </div>
              </div>
              <div className="bg-[#0B0F19]/80 border border-[#2A364F] rounded-xl p-2.5 space-y-1">
                <div className="text-[10px] uppercase font-bold text-[#64748B]">Warehouse</div>
                <div className="text-xs font-bold text-[#10B981] flex items-center gap-1">
                  <Database className="w-3.5 h-3.5 text-[#10B981]" />
                  DuckDB 600s
                </div>
              </div>
              <div className="bg-[#0B0F19]/80 border border-[#2A364F] rounded-xl p-2.5 space-y-1">
                <div className="text-[10px] uppercase font-bold text-[#64748B]">Trust Score</div>
                <div className="text-xs font-bold text-[#38BDF8] flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-[#38BDF8]" />
                  94.6 / 100
                </div>
              </div>
              <div className="bg-[#0B0F19]/80 border border-[#2A364F] rounded-xl p-2.5 space-y-1">
                <div className="text-[10px] uppercase font-bold text-[#64748B]">SQL Guard</div>
                <div className="text-xs font-bold text-[#F59E0B] flex items-center gap-1">
                  <Shield className="w-3.5 h-3.5 text-[#F59E0B]" />
                  Read-Only
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── INTERACTIVE NATURAL LANGUAGE QUERY BAR ─────────────────── */}
        <div className="bg-[#151D2E] border border-[#2A364F] rounded-2xl p-5 space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <label htmlFor="workbench-query-input" className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Search className="w-4 h-4 text-[#38BDF8]" />
              Natural Language Policy Inquiry
            </label>
            <div className="flex items-center gap-2 text-xs">
              <span className="font-mono text-[11px] text-[#64748B] bg-[#0B0F19] px-2.5 py-1 rounded-lg border border-[#2A364F]">
                Session: {sessionId}
              </span>
              <button
                onClick={handleResetSession}
                className="text-[11px] text-[#94A3B8] hover:text-white flex items-center gap-1 bg-[#0B0F19] hover:bg-[#1E293B] px-2.5 py-1 rounded-lg border border-[#2A364F] transition-colors"
                title="Reset conversation state"
              >
                <RotateCcw className="w-3 h-3" />
                Reset
              </button>
            </div>
          </div>

          <div className="relative">
            <input
              id="workbench-query-input"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(query);
                }
              }}
              placeholder="Type any educational question (e.g., Which district has the lowest attendance rate?)..."
              className="w-full bg-[#0B0F19] border border-[#2A364F] focus:border-[#38BDF8] rounded-xl pl-4 pr-32 py-3.5 text-sm text-white placeholder-[#64748B] focus:outline-none focus:ring-2 focus:ring-[#0284C7]/20 transition-all shadow-inner"
            />
            <div className="absolute right-2 top-2 flex items-center gap-2">
              {query && (
                <button
                  onClick={() => setQuery("")}
                  className="text-xs text-[#64748B] hover:text-white px-2 py-1.5 transition-colors"
                >
                  Clear
                </button>
              )}
              <button
                onClick={() => handleSubmit(query)}
                disabled={isLoading || !query.trim()}
                className="px-4 py-2 bg-gradient-to-r from-[#0284C7] to-[#0369A1] hover:from-[#0369A1] hover:to-[#0284C7] disabled:opacity-40 text-white text-xs font-semibold rounded-lg flex items-center gap-2 transition-all shadow-md shadow-[#0284C7]/20"
              >
                {isLoading ? (
                  <span>Reasoning...</span>
                ) : (
                  <>
                    <span>Dispatch</span>
                    <Send className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* ── ANIMATED REASONING PIPELINE STEPPER ────────────────────── */}
        {isLoading && (
          <div className="bg-[#151D2E] border border-[#38BDF8]/40 rounded-2xl p-5 shadow-xl animate-in fade-in duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Brain className="w-4 h-4 text-[#8B5CF6] animate-pulse" />
                Two-Stage Autonomous Reasoning Pipeline
              </div>
              <span className="text-[11px] font-mono text-[#38BDF8] animate-pulse">
                Active Execution
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
              {PIPELINE_STEPS.map((step, i) => {
                const StepIcon = step.icon;
                const isActive = i === pipelineStep;
                const isDone = i < pipelineStep;
                return (
                  <div
                    key={i}
                    className={`flex flex-col p-3 rounded-xl border text-xs transition-all duration-300 ${
                      isActive
                        ? "bg-[#0B0F19] border-[#38BDF8] text-white shadow-lg shadow-[#0284C7]/20 scale-[1.02]"
                        : isDone
                        ? "bg-[#10B981]/10 border-[#10B981]/30 text-[#10B981]"
                        : "bg-[#0B0F19]/40 border-[#2A364F]/50 text-[#64748B]"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <StepIcon className={`w-4 h-4 shrink-0 ${isActive ? "animate-pulse" : ""}`} style={{ color: isActive ? step.color : undefined }} />
                      <span className="text-[10px] font-mono opacity-70">0{i + 1}</span>
                    </div>
                    <div className="font-semibold truncate">{step.label}</div>
                    <div className="text-[10px] opacity-70 truncate mt-0.5">{step.detail}</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── ERROR DISPLAY ─────────────────────────────────────────── */}
        {error && (
          <div className="bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-xl p-4 text-xs text-[#FCA5A5] flex items-center gap-2 shadow-md">
            <ShieldAlert className="w-4 h-4 shrink-0 text-[#EF4444]" />
            <span>{error}</span>
          </div>
        )}

        {/* ── FALLBACK ADVISORY BANNER ──────────────────────────────── */}
        {response && response.reasoning_mode === "deterministic_fallback" && (
          <div className="bg-[#F59E0B]/10 border border-[#F59E0B]/30 rounded-xl p-4 text-xs text-[#FDE68A] flex items-center gap-2 shadow-md">
            <Zap className="w-4 h-4 shrink-0 text-[#F59E0B]" />
            <span>
              External LLM endpoint cooldown active. Automatically routed to the zero-latency Governed Semantic Engine. All facts remain strictly DuckDB-grounded.
            </span>
          </div>
        )}

        {/* ── DISCOVERY SHOWCASE (EMPTY STATE / BEFORE QUERY) ───────── */}
        {!response && !isLoading && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Quick Metrics Audit Bar */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-4 text-center">
                <div className="text-[11px] font-medium text-[#94A3B8] uppercase">Monitored Cohort</div>
                <div className="text-xl font-black text-white mt-1">600 Schools</div>
                <div className="text-[10px] text-[#64748B] mt-0.5">23 Administrative Districts</div>
              </div>
              <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-4 text-center">
                <div className="text-[11px] font-medium text-[#94A3B8] uppercase">State Attendance</div>
                <div className="text-xl font-black text-[#10B981] mt-1">79.4%</div>
                <div className="text-[10px] text-[#64748B] mt-0.5">Normalized across sessions</div>
              </div>
              <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-4 text-center">
                <div className="text-[11px] font-medium text-[#94A3B8] uppercase">FLN Academic Baseline</div>
                <div className="text-xl font-black text-[#38BDF8] mt-1">66.2 / 100</div>
                <div className="text-[10px] text-[#64748B] mt-0.5">Foundational literacy & math</div>
              </div>
              <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-4 text-center">
                <div className="text-[11px] font-medium text-[#94A3B8] uppercase">Data Trust Score</div>
                <div className="text-xl font-black text-[#8B5CF6] mt-1">94.6 / 100</div>
                <div className="text-[10px] text-[#64748B] mt-0.5">37,974 trusted warehouse records</div>
              </div>
            </div>

            {/* Showcase Mission Cards */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Activity className="w-4 h-4 text-[#38BDF8]" />
                  Curated Decision Intelligence Missions
                </div>
                <span className="text-[11px] text-[#64748B]">Click any card to dispatch instant analysis</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {SHOWCASE_MISSIONS.map((mission, idx) => {
                  const Icon = mission.icon;
                  return (
                    <div
                      key={idx}
                      onClick={() => {
                        setQuery(mission.prompt);
                        handleSubmit(mission.prompt);
                      }}
                      className="group cursor-pointer rounded-2xl bg-[#151D2E] hover:bg-[#1A2438] border border-[#2A364F] hover:border-[#38BDF8]/50 p-5 space-y-3.5 transition-all duration-200 shadow-lg hover:shadow-[#0284C7]/15 hover:-translate-y-0.5 flex flex-col justify-between"
                    >
                      <div className="space-y-2.5">
                        <div className="flex items-center justify-between">
                          <div
                            className="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-md transition-transform group-hover:scale-110"
                            style={{ backgroundColor: `${mission.color}25`, color: mission.color, border: `1px solid ${mission.color}40` }}
                          >
                            <Icon className="w-4 h-4" />
                          </div>
                          <span className="text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded-full bg-[#0B0F19] text-[#94A3B8] border border-[#2A364F]">
                            {mission.tag}
                          </span>
                        </div>

                        <div>
                          <div className="text-[11px] font-bold uppercase tracking-wider text-[#64748B]">
                            {mission.category}
                          </div>
                          <h3 className="text-sm font-bold text-white group-hover:text-[#38BDF8] transition-colors mt-0.5">
                            {mission.title}
                          </h3>
                        </div>

                        <p className="text-xs text-[#94A3B8] leading-relaxed">
                          {mission.description}
                        </p>
                      </div>

                      <div className="pt-3 border-t border-[#2A364F]/60 flex items-center justify-between text-xs text-[#38BDF8] font-medium">
                        <span className="truncate max-w-[220px] text-[#94A3B8] group-hover:text-white transition-colors">
                          &ldquo;{mission.prompt}&rdquo;
                        </span>
                        <ChevronRight className="w-4 h-4 shrink-0 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Architecture Provenance Explanation Card */}
            <div className="bg-[#151D2E]/60 border border-[#2A364F] rounded-2xl p-5 space-y-3">
              <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-[#10B981]" />
                How Governed AI Reasoning Operates
              </div>
              <p className="text-xs text-[#94A3B8] leading-relaxed">
                The EduPulse AI Analyst never hallucinates facts or runs unrestrained SQL. It translates questions into formal Pydantic intents, validates every metric against the canonical metric registry, executes strictly read-only parameterized queries against DuckDB, and subjects all generated text to post-synthesis causal verb and numeric claim audits.
              </p>
            </div>
          </div>
        )}

        {/* ── FULL DECISION INTELLIGENCE RESULT WORKBENCH ───────────── */}
        {response && (
          <div className="space-y-6 animate-in fade-in duration-200">
            {/* Top Intelligence KPI Bar */}
            <div className="bg-[#151D2E] border border-[#2A364F] rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-lg">
              <div className="flex flex-wrap items-center gap-2.5">
                <span className={`text-xs uppercase font-bold px-3 py-1 rounded-lg flex items-center gap-1.5 ${
                  response.reasoning_mode === "llama_3.1"
                    ? "bg-[#8B5CF6]/20 text-[#A78BFA] border border-[#8B5CF6]/40"
                    : "bg-[#0284C7]/20 text-[#38BDF8] border border-[#0284C7]/40"
                }`}>
                  {response.reasoning_mode === "llama_3.1" ? (
                    <><Brain className="w-3.5 h-3.5" /> Llama 3.1 Synthesis</>
                  ) : (
                    <><Cpu className="w-3.5 h-3.5" /> Governed Engine</>
                  )}
                </span>

                <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-[#0B0F19] text-[#94A3B8] border border-[#2A364F]">
                  Intent: <strong className="text-white">{response.intent_type}</strong>
                </span>

                <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-[#0B0F19] text-[#94A3B8] border border-[#2A364F]">
                  Metric: <strong className="text-[#10B981]">{response.primary_metric_label || response.primary_metric}</strong>
                </span>
              </div>

              <div className="flex items-center gap-3 text-xs text-[#94A3B8] font-mono">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-[#64748B]" />
                  Total: {response.timings_ms?.total_duration_ms || 0}ms
                </span>
                <span className="text-[#38BDF8]">
                  SQL: {response.timings_ms?.sql_duration_ms || 0}ms
                </span>
                {response.timings_ms?.synthesis_duration_ms != null && (
                  <span className="text-[#A78BFA]">
                    LLM: {response.timings_ms.synthesis_duration_ms}ms
                  </span>
                )}
                <span className="text-[#10B981]">
                  N = {response.evidence_count} rows
                </span>
              </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex border-b border-[#2A364F] space-x-2">
              <button
                onClick={() => setActiveTab("analysis")}
                className={`pb-3 px-4 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition-all ${
                  activeTab === "analysis"
                    ? "border-[#38BDF8] text-[#38BDF8]"
                    : "border-transparent text-[#94A3B8] hover:text-white"
                }`}
              >
                <FileText className="w-4 h-4" />
                Executive Finding
              </button>

              <button
                onClick={() => setActiveTab("visuals")}
                className={`pb-3 px-4 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition-all ${
                  activeTab === "visuals"
                    ? "border-[#38BDF8] text-[#38BDF8]"
                    : "border-transparent text-[#94A3B8] hover:text-white"
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                Visual Evidence
              </button>

              <button
                onClick={() => setActiveTab("actions")}
                className={`pb-3 px-4 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition-all ${
                  activeTab === "actions"
                    ? "border-[#38BDF8] text-[#38BDF8]"
                    : "border-transparent text-[#94A3B8] hover:text-white"
                }`}
              >
                <Target className="w-4 h-4" />
                Recommended Protocol ({response.recommendations?.length || 0})
              </button>

              <button
                onClick={() => setActiveTab("evidence")}
                className={`pb-3 px-4 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition-all ${
                  activeTab === "evidence"
                    ? "border-[#38BDF8] text-[#38BDF8]"
                    : "border-transparent text-[#94A3B8] hover:text-white"
                }`}
              >
                <Database className="w-4 h-4" />
                Executed Rows ({response.evidence_count})
              </button>
            </div>

            {/* Tab Contents Grid: 8 Cols Left + 4 Cols Right */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* ── LEFT COLUMN (8 COLS) ───────────────────────────── */}
              <div className="lg:col-span-8 space-y-6">
                {/* TAB 1: EXECUTIVE ANALYSIS */}
                {activeTab === "analysis" && (
                  <div className="space-y-6">
                    {/* Executive Narrative Box */}
                    <div className="bg-[#151D2E] border border-[#2A364F] rounded-2xl p-6 space-y-4 shadow-xl">
                      <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                        <FileCheck2 className="w-4 h-4 text-[#38BDF8]" />
                        Evidence-Grounded Policy Finding
                      </div>

                      <div className="bg-[#0B0F19] border border-[#2A364F] rounded-xl p-5 text-sm text-[#E2E8F0] leading-relaxed whitespace-pre-line font-sans shadow-inner">
                        {response.answer}
                      </div>

                      {/* Governance Caveats */}
                      {response.caveats && response.caveats.length > 0 && (
                        <div className="bg-[#F59E0B]/10 border border-[#F59E0B]/30 rounded-xl p-4 space-y-2">
                          <div className="text-xs font-bold text-[#FBBF24] flex items-center gap-2 uppercase">
                            <AlertTriangle className="w-4 h-4" />
                            Governed Analytical Caveats:
                          </div>
                          <ul className="list-disc list-inside text-xs text-[#FDE68A] space-y-1">
                            {response.caveats.map((c, i) => (
                              <li key={i}>{c}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* TAB 2: VISUAL EVIDENCE */}
                {activeTab === "visuals" && (
                  <div className="bg-[#151D2E] border border-[#2A364F] rounded-2xl p-6 space-y-4 shadow-xl">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-base font-bold text-white flex items-center gap-2">
                          <BarChart3 className="w-5 h-5 text-[#38BDF8]" />
                          {response.chart_plan?.title || "Analytical Visualization"}
                        </h3>
                        <p className="text-xs text-[#94A3B8] mt-0.5">{response.chart_plan?.subtitle}</p>
                      </div>
                      <span className="text-[10px] font-mono text-[#64748B] uppercase bg-[#0B0F19] px-2.5 py-1 rounded-md border border-[#2A364F]">
                        {response.chart_plan?.chart_type}
                      </span>
                    </div>

                    <div className="h-80 w-full pt-4">
                      {response.chart_plan?.chart_type === "scatter" ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#2A364F" />
                            <XAxis type="number" dataKey="attendance" name="Attendance" stroke="#64748B" fontSize={11} unit="%" />
                            <YAxis type="number" dataKey="academic_score" name="Academic FLN" stroke="#64748B" fontSize={11} />
                            <Tooltip contentStyle={{ backgroundColor: "#151D2E", borderColor: "#2A364F", fontSize: "11px" }} />
                            <Scatter name="Schools" data={response.chart_plan.data} fill="#10B981" />
                          </ScatterChart>
                        </ResponsiveContainer>
                      ) : response.chart_plan?.chart_type === "horizontal_bar" ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart layout="vertical" data={response.chart_plan.data} margin={{ top: 5, right: 30, left: 60, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#2A364F" horizontal={false} />
                            <XAxis type="number" stroke="#64748B" fontSize={11} />
                            <YAxis dataKey={response.chart_plan.x_key} type="category" stroke="#64748B" fontSize={10} width={80} />
                            <Tooltip contentStyle={{ backgroundColor: "#151D2E", borderColor: "#2A364F", fontSize: "11px" }} />
                            <Bar dataKey={response.chart_plan.y_keys[0]} fill="#F59E0B" radius={[0, 4, 4, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      ) : (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={response.chart_plan?.data} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#2A364F" vertical={false} />
                            <XAxis dataKey={response.chart_plan?.x_key} stroke="#64748B" fontSize={11} />
                            <YAxis stroke="#64748B" fontSize={11} />
                            <Tooltip contentStyle={{ backgroundColor: "#151D2E", borderColor: "#2A364F", fontSize: "11px" }} />
                            {response.chart_plan?.y_keys?.map((k, i) => (
                              <Bar
                                key={k}
                                dataKey={k}
                                name={response.chart_plan?.series_labels?.[k] || k}
                                fill={i === 0 ? "#0284C7" : "#10B981"}
                                radius={[4, 4, 0, 0]}
                              />
                            ))}
                          </BarChart>
                        </ResponsiveContainer>
                      )}
                    </div>
                  </div>
                )}

                {/* TAB 3: RECOMMENDED PROTOCOL */}
                {activeTab === "actions" && (
                  <div className="bg-[#151D2E] border border-[#2A364F] rounded-2xl p-6 space-y-4 shadow-xl">
                    <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Target className="w-4 h-4 text-[#10B981]" />
                      Operational Intervention Action Catalog
                    </div>

                    <div className="space-y-3">
                      {response.recommendations?.map((action, idx) => (
                        <div key={idx} className="bg-[#0B0F19] border border-[#2A364F] rounded-xl p-4 space-y-2.5">
                          <div className="flex items-center justify-between">
                            <div className="text-xs font-bold text-white flex items-center gap-2">
                              <span className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded ${
                                action.urgency === "IMMEDIATE" ? "bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/30" :
                                action.urgency === "HIGH" ? "bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30" :
                                "bg-[#0284C7]/20 text-[#38BDF8] border border-[#0284C7]/30"
                              }`}>
                                {action.urgency}
                              </span>
                              {action.action_title}
                            </div>
                            <span className="text-[11px] font-mono text-[#64748B]">{action.action_code}</span>
                          </div>
                          <p className="text-xs text-[#94A3B8] leading-relaxed">{action.rationale}</p>
                          <div className="flex flex-wrap items-center justify-between text-xs text-[#64748B] pt-2 border-t border-[#2A364F]/50">
                            <span>Target: <strong className="text-white">{action.target_entity}</strong></span>
                            <span>Responsible: <strong className="text-[#38BDF8]">{action.owner}</strong></span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* TAB 4: EXECUTED ROWS */}
                {activeTab === "evidence" && (
                  <div className="bg-[#151D2E] border border-[#2A364F] rounded-2xl p-6 space-y-4 shadow-xl">
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                        <Layers className="w-4 h-4 text-[#38BDF8]" />
                        Executed Warehouse Evidence Rows ({response.evidence_count})
                      </div>
                      <span className="text-[11px] text-[#64748B]">Showing preview of executed DuckDB dataset</span>
                    </div>

                    <div className="overflow-x-auto border border-[#2A364F] rounded-xl max-h-96">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-[#0B0F19] text-[#64748B] border-b border-[#2A364F] sticky top-0 font-mono">
                          <tr>
                            {response.evidence_records?.[0] && Object.keys(response.evidence_records[0]).slice(0, 6).map((col) => (
                              <th key={col} className="px-3 py-2 uppercase font-semibold">
                                {col.replace(/_/g, " ")}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#2A364F]/40 bg-[#151D2E]/40 font-mono">
                          {response.evidence_records?.slice(0, 20).map((row, rIdx) => (
                            <tr key={rIdx} className="hover:bg-[#1E293B]/60 transition-colors">
                              {Object.values(row).slice(0, 6).map((val: any, cIdx) => (
                                <td key={cIdx} className="px-3 py-2 text-white truncate max-w-[150px]">
                                  {String(val)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Contextual Follow-Up Suggestions */}
                {response.follow_up_questions && response.follow_up_questions.length > 0 && (
                  <div className="bg-[#151D2E] border border-[#2A364F] rounded-2xl p-4 space-y-2.5 shadow-md">
                    <div className="text-xs font-bold text-[#94A3B8] uppercase tracking-wider flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-[#38BDF8]" />
                      Contextual Follow-Up Inquiries:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {response.follow_up_questions.map((fq, i) => (
                        <button
                          key={i}
                          onClick={() => {
                            setQuery(fq);
                            handleSubmit(fq);
                          }}
                          className="text-xs bg-[#0B0F19] hover:bg-[#1E293B] border border-[#2A364F] hover:border-[#38BDF8]/50 text-[#94A3B8] hover:text-white px-3.5 py-2 rounded-xl flex items-center gap-1.5 transition-all shadow-sm"
                        >
                          <span>{fq}</span>
                          <ChevronRight className="w-3.5 h-3.5 text-[#38BDF8]" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* ── RIGHT COLUMN (4 COLS) ──────────────────────────── */}
              <div className="lg:col-span-4 space-y-6">
                {/* Grounding & Verification Card */}
                <div className="bg-[#151D2E] border border-[#2A364F] rounded-2xl p-5 space-y-4 shadow-xl">
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <FileCheck2 className="w-4 h-4 text-[#10B981]" />
                      Grounding Integrity Audit
                    </div>
                    <span className="text-[10px] font-mono text-[#64748B]">{response.query_id}</span>
                  </div>

                  <div className="bg-[#0B0F19] border border-[#2A364F] rounded-xl p-4 space-y-2.5 shadow-inner">
                    <div className="flex items-center gap-2 text-xs font-bold text-white">
                      <CheckCircle className="w-4 h-4 text-[#10B981] shrink-0" />
                      <span>100% Governed SQL Compilation</span>
                    </div>
                    <p className="text-xs text-[#94A3B8] leading-relaxed">
                      Every single numeric figure is cross-verified against DuckDB executed records. Zero ungrounded generation.
                    </p>
                    <div className="text-[11px] font-mono text-[#64748B] pt-1.5 border-t border-[#2A364F]/50">
                      Sample Size: N = {response.evidence_count} records
                    </div>
                  </div>

                  {/* Feedback Action */}
                  <div className="pt-2 border-t border-[#2A364F] space-y-2.5">
                    <div className="text-xs font-semibold text-[#94A3B8] flex items-center justify-between">
                      <span>Analyst Precision Feedback:</span>
                      {feedbackGiven[response.query_id] !== undefined && (
                        <span className="text-[11px] text-[#10B981] font-semibold">Feedback Recorded</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleFeedback(true)}
                        className={`flex-1 py-2 rounded-xl border text-xs font-medium flex items-center justify-center gap-2 transition-colors ${
                          feedbackGiven[response.query_id] === true
                            ? "bg-[#10B981]/20 border-[#10B981] text-[#10B981]"
                            : "bg-[#0B0F19] hover:bg-[#1E293B] border-[#2A364F] text-[#94A3B8]"
                        }`}
                      >
                        <ThumbsUp className="w-3.5 h-3.5" />
                        Accurate
                      </button>
                      <button
                        onClick={() => handleFeedback(false)}
                        className={`flex-1 py-2 rounded-xl border text-xs font-medium flex items-center justify-center gap-2 transition-colors ${
                          feedbackGiven[response.query_id] === false
                            ? "bg-[#EF4444]/20 border-[#EF4444] text-[#EF4444]"
                            : "bg-[#0B0F19] hover:bg-[#1E293B] border-[#2A364F] text-[#94A3B8]"
                        }`}
                      >
                        <ThumbsDown className="w-3.5 h-3.5" />
                        Flag Review
                      </button>
                    </div>
                  </div>
                </div>

                {/* Verifiable Citations */}
                {response.citations && response.citations.length > 0 && (
                  <div className="bg-[#151D2E] border border-[#2A364F] rounded-2xl p-5 space-y-3 shadow-xl">
                    <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Database className="w-4 h-4 text-[#38BDF8]" />
                      Verifiable Citations ({response.citations.length})
                    </div>
                    <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                      {response.citations.map((c, i) => (
                        <div key={i} className="bg-[#0B0F19] border border-[#2A364F] rounded-xl p-3 space-y-1.5 text-xs">
                          <div className="flex items-center justify-between">
                            <strong className="text-white font-mono">{c.record_identifier}</strong>
                            <span className="text-[11px] text-[#10B981] font-bold">
                              {c.value !== null ? `${c.value} ${c.unit}` : "N/A"}
                            </span>
                          </div>
                          <div className="text-[11px] text-[#94A3B8] flex items-center justify-between">
                            <span>View: <code className="text-[#38BDF8]">{c.source_view}</code></span>
                            {c.district && <span>{c.district}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
