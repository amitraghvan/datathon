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
    color: "#DC2626",
  },
  {
    category: "Statistical Association",
    icon: TrendingUp,
    title: "Daily Attendance vs. FLN Score Correlation",
    description: "Verify non-causal bivariate Pearson (r = 0.453) and Spearman correlation across 600 institutions.",
    prompt: "Does student attendance correlate with FLN academic scores?",
    tag: "Non-Causal",
    color: "#059669",
  },
  {
    category: "Procurement & Welfare",
    icon: PieChart,
    title: "Mid-Day Meal Spend Outlier Detection",
    description: "Audit commodity cost variance ratios and flag peer group benchmark exceptions without accusations.",
    prompt: "Are there any Mid-Day Meal procurement cost outliers?",
    tag: "Nutrition",
    color: "#D97706",
  },
  {
    category: "Infrastructure Impact",
    icon: Building,
    title: "Amenity Deficits & Learning Efficacy",
    description: "Evaluate observational score differences for schools with complete electricity vs. unverified status.",
    prompt: "How do schools with electricity compare on academic performance?",
    tag: "Amenities",
    color: "#7C3AED",
  },
  {
    category: "Data Trust & Governance",
    icon: ShieldCheck,
    title: "Warehouse Quality Gates & Quarantine Audit",
    description: "Audit the 10 automated data quality gates, 37,974 trusted rows, and 1,929 quarantined anomaly records.",
    prompt: "What is the data trust score and profile completeness across schools?",
    tag: "Governance",
    color: "#0891B2",
  },
];

const PIPELINE_STEPS = [
  { label: "Semantic Graph Parsing", icon: Brain, color: "#7C3AED", detail: "Resolving intent & canonical entities" },
  { label: "Governed SQL Compilation", icon: Search, color: "#0284C7", detail: "Read-only DuckDB view query" },
  { label: "DuckDB Warehouse Execution", icon: Database, color: "#059669", detail: "Retrieving canonical evidence records" },
  { label: "Llama 3.1 Answer Synthesis", icon: Cpu, color: "#D97706", detail: "Formulating grounded executive findings" },
  { label: "Claim & Causal Audit", icon: Shield, color: "#059669", detail: "Anti-hallucination verification" },
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
    <div className="flex-1 flex flex-col min-h-screen bg-[#F8FAFC]">
      <Header
        title="AI Analyst — Decision Intelligence Workbench"
        subtitle="Autonomous Graph-First reasoning agent grounded strictly in canonical DuckDB warehouse views with zero-hallucination provenance."
      />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* ── TOP HERO BANNER & LIVE SYSTEM STATUS ───────────────────── */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xs">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-sky-50 text-sky-700 border border-sky-200">
                  <Sparkles className="w-3 h-3 text-sky-600" />
                  Autonomous Decision Intelligence Engine
                </span>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-medium text-emerald-700 bg-emerald-50 border border-emerald-200">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  Live Grounded
                </span>
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                Enterprise Autonomous Education Analyst
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 max-w-2xl leading-relaxed">
                Query school triage queues, examine peer benchmark anomalies, and audit retention drivers with guaranteed zero-hallucination execution over canonical DuckDB data.
              </p>
            </div>

            {/* Quick Status Chips Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 shrink-0">
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 space-y-1">
                <div className="text-[10px] uppercase font-bold text-slate-500">Reasoning Model</div>
                <div className="text-xs font-bold text-slate-900 flex items-center gap-1">
                  <Brain className="w-3.5 h-3.5 text-purple-600" />
                  Llama 3.1
                </div>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 space-y-1">
                <div className="text-[10px] uppercase font-bold text-slate-500">Canonical Warehouse</div>
                <div className="text-xs font-bold text-emerald-700 flex items-center gap-1">
                  <Database className="w-3.5 h-3.5 text-emerald-600" />
                  DuckDB 600s
                </div>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 space-y-1">
                <div className="text-[10px] uppercase font-bold text-slate-500">Trust Score</div>
                <div className="text-xs font-bold text-sky-700 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-sky-600" />
                  94.6 / 100
                </div>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 space-y-1">
                <div className="text-[10px] uppercase font-bold text-slate-500">SQL Guard</div>
                <div className="text-xs font-bold text-amber-700 flex items-center gap-1">
                  <Shield className="w-3.5 h-3.5 text-amber-600" />
                  Read-Only
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── INTERACTIVE NATURAL LANGUAGE QUERY BAR ─────────────────── */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-3.5 shadow-2xs">
          <div className="flex items-center justify-between">
            <label htmlFor="workbench-query-input" className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Search className="w-4 h-4 text-sky-600" />
              Natural Language Policy Inquiry
            </label>
            <div className="flex items-center gap-2 text-xs">
              <span className="font-mono text-[11px] text-slate-500 bg-slate-50 px-2.5 py-1 rounded border border-slate-200">
                Session Active
              </span>
              <button
                onClick={handleResetSession}
                className="text-[11px] text-slate-600 hover:text-slate-900 flex items-center gap-1 bg-slate-50 hover:bg-slate-100 px-2.5 py-1 rounded border border-slate-200 transition-colors"
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
              placeholder="Ask about attendance, academics, welfare, infrastructure, procurement or intervention priorities..."
              className="w-full bg-slate-50 border border-slate-200 focus:bg-white focus:border-sky-600 rounded-lg pl-4 pr-32 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all"
            />
            <div className="absolute right-1.5 top-1.5 flex items-center gap-2">
              {query && (
                <button
                  onClick={() => setQuery("")}
                  className="text-xs text-slate-400 hover:text-slate-700 px-2 py-1.5 transition-colors"
                >
                  Clear
                </button>
              )}
              <button
                onClick={() => handleSubmit(query)}
                disabled={isLoading || !query.trim()}
                className="px-4 py-2 bg-sky-700 hover:bg-sky-800 disabled:opacity-40 text-white text-xs font-semibold rounded-md flex items-center gap-2 transition-all shadow-2xs"
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
          <div className="bg-white border border-sky-300 rounded-xl p-5 shadow-2xs animate-in fade-in duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <Brain className="w-4 h-4 text-purple-600 animate-pulse" />
                Two-Stage Autonomous Reasoning Pipeline
              </div>
              <span className="text-[11px] font-mono text-sky-700 font-semibold animate-pulse">
                Active Execution
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-5 gap-2.5">
              {PIPELINE_STEPS.map((step, i) => {
                const StepIcon = step.icon;
                const isActive = i === pipelineStep;
                const isDone = i < pipelineStep;
                return (
                  <div
                    key={i}
                    className={`flex flex-col p-3 rounded-lg border text-xs transition-all duration-300 ${
                      isActive
                        ? "bg-sky-50/80 border-sky-400 text-sky-950 font-medium shadow-2xs"
                        : isDone
                        ? "bg-emerald-50/60 border-emerald-200 text-emerald-800"
                        : "bg-slate-50 border-slate-200 text-slate-500"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <StepIcon className={`w-4 h-4 shrink-0 ${isActive ? "animate-pulse" : ""}`} style={{ color: isActive ? step.color : undefined }} />
                      <span className="text-[10px] font-mono opacity-70">0{i + 1}</span>
                    </div>
                    <div className="font-bold truncate text-slate-900">{step.label}</div>
                    <div className="text-[10px] text-slate-500 truncate mt-0.5">{step.detail}</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── ERROR DISPLAY ─────────────────────────────────────────── */}
        {error && (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-xs text-rose-800 flex items-center gap-2 shadow-2xs">
            <ShieldAlert className="w-4 h-4 shrink-0 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        {/* ── FALLBACK ADVISORY BANNER ──────────────────────────────── */}
        {response && response.reasoning_mode === "deterministic_fallback" && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-800 flex items-center gap-2 shadow-2xs">
            <Zap className="w-4 h-4 shrink-0 text-amber-600" />
            <span>
              External LLM endpoint cooldown active. Automatically routed to the zero-latency Governed Semantic Engine. All facts remain strictly DuckDB-grounded.
            </span>
          </div>
        )}

        {/* ── DISCOVERY SHOWCASE (EMPTY STATE / BEFORE QUERY) ───────── */}
        {!response && !isLoading && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Quick Metrics Audit Bar */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
              <div className="bg-white border border-slate-200 rounded-xl p-4 text-center shadow-2xs">
                <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Monitored Cohort</div>
                <div className="text-xl font-bold text-slate-900 mt-1">600 Schools</div>
                <div className="text-[10px] text-slate-500 mt-0.5">23 Administrative Districts</div>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-4 text-center shadow-2xs">
                <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">State Attendance</div>
                <div className="text-xl font-bold text-emerald-700 mt-1">79.4%</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Normalized across sessions</div>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-4 text-center shadow-2xs">
                <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">FLN Academic Baseline</div>
                <div className="text-xl font-bold text-sky-700 mt-1">66.2 / 100</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Foundational literacy & math</div>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-4 text-center shadow-2xs">
                <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Data Trust Score</div>
                <div className="text-xl font-bold text-purple-700 mt-1">94.6 / 100</div>
                <div className="text-[10px] text-slate-500 mt-0.5">37,974 trusted warehouse records</div>
              </div>
            </div>

            {/* Showcase Mission Cards */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  <Activity className="w-4 h-4 text-sky-600" />
                  Curated Decision Intelligence Missions
                </div>
                <span className="text-[11px] text-slate-500">Click any card to dispatch instant analysis</span>
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
                      className="group cursor-pointer rounded-xl bg-white hover:bg-slate-50/80 border border-slate-200 hover:border-slate-300 p-5 space-y-3 transition-all duration-200 shadow-2xs hover:shadow-xs flex flex-col justify-between"
                    >
                      <div className="space-y-2.5">
                        <div className="flex items-center justify-between">
                          <div
                            className="w-9 h-9 rounded-lg flex items-center justify-center text-white shadow-2xs transition-transform group-hover:scale-105"
                            style={{ backgroundColor: `${mission.color}15`, color: mission.color, border: `1px solid ${mission.color}30` }}
                          >
                            <Icon className="w-4 h-4" />
                          </div>
                          <span className="text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                            {mission.tag}
                          </span>
                        </div>

                        <div>
                          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                            {mission.category}
                          </div>
                          <h3 className="text-sm font-bold text-slate-900 group-hover:text-sky-700 transition-colors mt-0.5">
                            {mission.title}
                          </h3>
                        </div>

                        <p className="text-xs text-slate-500 leading-relaxed">
                          {mission.description}
                        </p>
                      </div>

                      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-sky-700 font-medium">
                        <span className="truncate max-w-[220px] text-slate-600 group-hover:text-slate-900 transition-colors">
                          &ldquo;{mission.prompt}&rdquo;
                        </span>
                        <ChevronRight className="w-4 h-4 shrink-0 group-hover:translate-x-0.5 transition-transform text-slate-400 group-hover:text-sky-600" />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Architecture Provenance Explanation Card */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-2 shadow-2xs">
              <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                How Governed AI Reasoning Operates
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                The EduPulse AI Analyst never hallucinates facts or runs unrestrained SQL. It translates questions into formal Pydantic intents, validates every metric against the canonical metric registry, executes strictly read-only parameterized queries against DuckDB, and subjects all generated text to post-synthesis causal verb and numeric claim audits.
              </p>
            </div>
          </div>
        )}

        {/* ── FULL DECISION INTELLIGENCE RESULT WORKBENCH ───────────── */}
        {response && (
          <div className="space-y-6 animate-in fade-in duration-200">
            {/* Top Intelligence KPI Bar */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-2xs">
              <div className="flex flex-wrap items-center gap-2.5">
                <span className={`text-xs uppercase font-bold px-3 py-1 rounded-md flex items-center gap-1.5 ${
                  response.reasoning_mode === "llama_3.1"
                    ? "bg-purple-50 text-purple-700 border border-purple-200"
                    : "bg-sky-50 text-sky-700 border border-sky-200"
                }`}>
                  {response.reasoning_mode === "llama_3.1" ? (
                    <><Brain className="w-3.5 h-3.5" /> Llama 3.1 Synthesis</>
                  ) : (
                    <><Cpu className="w-3.5 h-3.5" /> Governed Engine</>
                  )}
                </span>

                <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-slate-50 text-slate-600 border border-slate-200">
                  Intent: <strong className="text-slate-900">{response.intent_type}</strong>
                </span>

                <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-slate-50 text-slate-600 border border-slate-200">
                  Metric: <strong className="text-emerald-700">{response.primary_metric_label || response.primary_metric}</strong>
                </span>
              </div>

              <div className="flex items-center gap-3 text-xs text-slate-500 font-mono">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-slate-400" />
                  Total: {response.timings_ms?.total_duration_ms || 0}ms
                </span>
                <span className="text-sky-700 font-semibold">
                  SQL: {response.timings_ms?.sql_duration_ms || 0}ms
                </span>
                {response.timings_ms?.synthesis_duration_ms != null && (
                  <span className="text-purple-700 font-semibold">
                    LLM: {response.timings_ms.synthesis_duration_ms}ms
                  </span>
                )}
                <span className="text-emerald-700 font-semibold">
                  N = {response.evidence_count} rows
                </span>
              </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex border-b border-slate-200 space-x-2">
              <button
                onClick={() => setActiveTab("analysis")}
                className={`pb-3 px-4 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition-all ${
                  activeTab === "analysis"
                    ? "border-sky-600 text-sky-700"
                    : "border-transparent text-slate-500 hover:text-slate-900"
                }`}
              >
                <FileText className="w-4 h-4" />
                Executive Finding
              </button>

              <button
                onClick={() => setActiveTab("visuals")}
                className={`pb-3 px-4 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition-all ${
                  activeTab === "visuals"
                    ? "border-sky-600 text-sky-700"
                    : "border-transparent text-slate-500 hover:text-slate-900"
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                Visual Evidence
              </button>

              <button
                onClick={() => setActiveTab("actions")}
                className={`pb-3 px-4 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition-all ${
                  activeTab === "actions"
                    ? "border-sky-600 text-sky-700"
                    : "border-transparent text-slate-500 hover:text-slate-900"
                }`}
              >
                <Target className="w-4 h-4" />
                Recommended Protocol ({response.recommendations?.length || 0})
              </button>

              <button
                onClick={() => setActiveTab("evidence")}
                className={`pb-3 px-4 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition-all ${
                  activeTab === "evidence"
                    ? "border-sky-600 text-sky-700"
                    : "border-transparent text-slate-500 hover:text-slate-900"
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
                    <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-4 shadow-2xs">
                      <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                        <FileCheck2 className="w-4 h-4 text-sky-600" />
                        Evidence-Grounded Policy Finding
                      </div>

                      <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 text-sm text-slate-900 leading-relaxed whitespace-pre-line font-sans">
                        {response.answer}
                      </div>

                      {/* Governance Caveats */}
                      {response.caveats && response.caveats.length > 0 && (
                        <div className="bg-amber-50/60 border border-amber-200 rounded-lg p-4 space-y-2">
                          <div className="text-xs font-bold text-amber-900 flex items-center gap-2 uppercase">
                            <AlertTriangle className="w-4 h-4 text-amber-600" />
                            Governed Analytical Caveats:
                          </div>
                          <ul className="list-disc list-inside text-xs text-amber-800 space-y-1">
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
                  <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-4 shadow-2xs">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                          <BarChart3 className="w-5 h-5 text-sky-600" />
                          {response.chart_plan?.title || "Analytical Visualization"}
                        </h3>
                        <p className="text-xs text-slate-500 mt-0.5">{response.chart_plan?.subtitle}</p>
                      </div>
                      <span className="text-[10px] font-mono text-slate-500 uppercase bg-slate-50 px-2.5 py-1 rounded border border-slate-200">
                        {response.chart_plan?.chart_type}
                      </span>
                    </div>

                    <div className="h-80 w-full pt-4">
                      {response.chart_plan?.chart_type === "scatter" ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                            <XAxis type="number" dataKey="attendance" name="Attendance" stroke="#64748B" fontSize={11} unit="%" />
                            <YAxis type="number" dataKey="academic_score" name="Academic FLN" stroke="#64748B" fontSize={11} />
                            <Tooltip contentStyle={{ backgroundColor: "#FFFFFF", borderColor: "#CBD5E1", fontSize: "11px", color: "#0F172A", boxShadow: "0 1px 3px rgba(0,0,0,0.08)" }} />
                            <Scatter name="Schools" data={response.chart_plan.data} fill="#059669" />
                          </ScatterChart>
                        </ResponsiveContainer>
                      ) : response.chart_plan?.chart_type === "horizontal_bar" ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart layout="vertical" data={response.chart_plan.data} margin={{ top: 5, right: 30, left: 60, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
                            <XAxis type="number" stroke="#64748B" fontSize={11} />
                            <YAxis dataKey={response.chart_plan.x_key} type="category" stroke="#64748B" fontSize={10} width={80} />
                            <Tooltip contentStyle={{ backgroundColor: "#FFFFFF", borderColor: "#CBD5E1", fontSize: "11px", color: "#0F172A", boxShadow: "0 1px 3px rgba(0,0,0,0.08)" }} />
                            <Bar dataKey={response.chart_plan.y_keys[0]} fill="#D97706" radius={[0, 4, 4, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      ) : (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={response.chart_plan?.data} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                            <XAxis dataKey={response.chart_plan?.x_key} stroke="#64748B" fontSize={11} />
                            <YAxis stroke="#64748B" fontSize={11} />
                            <Tooltip contentStyle={{ backgroundColor: "#FFFFFF", borderColor: "#CBD5E1", fontSize: "11px", color: "#0F172A", boxShadow: "0 1px 3px rgba(0,0,0,0.08)" }} />
                            {response.chart_plan?.y_keys?.map((k, i) => (
                              <Bar
                                key={k}
                                dataKey={k}
                                name={response.chart_plan?.series_labels?.[k] || k}
                                fill={i === 0 ? "#0284C7" : "#059669"}
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
                  <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-4 shadow-2xs">
                    <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                      <Target className="w-4 h-4 text-emerald-600" />
                      Operational Intervention Action Catalog
                    </div>

                    <div className="space-y-3">
                      {response.recommendations?.map((action, idx) => (
                        <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2.5">
                          <div className="flex items-center justify-between">
                            <div className="text-xs font-bold text-slate-900 flex items-center gap-2">
                              <span className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded ${
                                action.urgency === "IMMEDIATE" ? "bg-rose-50 text-rose-700 border border-rose-200" :
                                action.urgency === "HIGH" ? "bg-amber-50 text-amber-700 border border-amber-200" :
                                "bg-sky-50 text-sky-700 border border-sky-200"
                              }`}>
                                {action.urgency}
                              </span>
                              {action.action_title}
                            </div>
                            <span className="text-[11px] font-mono text-slate-500">{action.action_code}</span>
                          </div>
                          <p className="text-xs text-slate-600 leading-relaxed">{action.rationale}</p>
                          <div className="flex flex-wrap items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-200">
                            <span>Target: <strong className="text-slate-900">{action.target_entity}</strong></span>
                            <span>Responsible: <strong className="text-sky-700">{action.owner}</strong></span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* TAB 4: EXECUTED ROWS */}
                {activeTab === "evidence" && (
                  <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-4 shadow-2xs">
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                        <Layers className="w-4 h-4 text-sky-600" />
                        Executed Warehouse Evidence Rows ({response.evidence_count})
                      </div>
                      <span className="text-[11px] text-slate-500">Showing preview of executed DuckDB dataset</span>
                    </div>

                    <div className="overflow-x-auto border border-slate-200 rounded-lg max-h-96">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 sticky top-0 font-mono text-[10px] uppercase font-bold tracking-wider">
                          <tr>
                            {response.evidence_records?.[0] && Object.keys(response.evidence_records[0]).slice(0, 6).map((col) => (
                              <th key={col} className="px-3 py-2.5">
                                {col.replace(/_/g, " ")}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 font-mono text-slate-800">
                          {response.evidence_records?.slice(0, 20).map((row, rIdx) => (
                            <tr key={rIdx} className="hover:bg-slate-50/80 transition-colors">
                              {Object.values(row).slice(0, 6).map((val: any, cIdx) => (
                                <td key={cIdx} className="px-3 py-2 truncate max-w-[150px]">
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
                  <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-2.5 shadow-2xs">
                    <div className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-sky-600" />
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
                          className="text-xs bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 text-slate-700 hover:text-slate-900 px-3.5 py-2 rounded-lg flex items-center gap-1.5 transition-all shadow-2xs"
                        >
                          <span>{fq}</span>
                          <ChevronRight className="w-3.5 h-3.5 text-sky-600" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* ── RIGHT COLUMN (4 COLS) ──────────────────────────── */}
              <div className="lg:col-span-4 space-y-6">
                {/* Grounding & Verification Card */}
                <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                      <FileCheck2 className="w-4 h-4 text-emerald-600" />
                      Grounding Integrity Audit
                    </div>
                    <span className="text-[10px] font-mono text-slate-500">{response.query_id}</span>
                  </div>

                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2.5">
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-900">
                      <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>100% Governed SQL Compilation</span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      Every single numeric figure is cross-verified against DuckDB executed records. Zero ungrounded generation.
                    </p>
                    <div className="text-[11px] font-mono text-slate-500 pt-1.5 border-t border-slate-200">
                      Sample Size: N = {response.evidence_count} records
                    </div>
                  </div>

                  {/* Feedback Action */}
                  <div className="pt-2 border-t border-slate-200 space-y-2.5">
                    <div className="text-xs font-semibold text-slate-600 flex items-center justify-between">
                      <span>Analyst Precision Feedback:</span>
                      {feedbackGiven[response.query_id] !== undefined && (
                        <span className="text-[11px] text-emerald-700 font-semibold">Feedback Recorded</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleFeedback(true)}
                        className={`flex-1 py-2 rounded-lg border text-xs font-medium flex items-center justify-center gap-2 transition-colors ${
                          feedbackGiven[response.query_id] === true
                            ? "bg-emerald-50 border-emerald-300 text-emerald-700"
                            : "bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700"
                        }`}
                      >
                        <ThumbsUp className="w-3.5 h-3.5" />
                        Accurate
                      </button>
                      <button
                        onClick={() => handleFeedback(false)}
                        className={`flex-1 py-2 rounded-lg border text-xs font-medium flex items-center justify-center gap-2 transition-colors ${
                          feedbackGiven[response.query_id] === false
                            ? "bg-rose-50 border-rose-300 text-rose-700"
                            : "bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700"
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
                  <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-3 shadow-2xs">
                    <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                      <Database className="w-4 h-4 text-sky-600" />
                      Verifiable Citations ({response.citations.length})
                    </div>
                    <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                      {response.citations.map((c, i) => (
                        <div key={i} className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-1.5 text-xs">
                          <div className="flex items-center justify-between">
                            <strong className="text-slate-900 font-mono">{c.record_identifier}</strong>
                            <span className="text-[11px] text-emerald-700 font-bold">
                              {c.value !== null ? `${c.value} ${c.unit}` : "N/A"}
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-500 flex items-center justify-between">
                            <span>View: <code className="text-sky-700">{c.source_view}</code></span>
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
