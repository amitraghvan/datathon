"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  GraduationCap,
  Building2,
  Utensils,
  AlertTriangle,
  ShieldCheck,
  Bot,
  Layers,
  Database,
} from "lucide-react";
import { cn } from "@/lib/utils/formatters";

const navigationItems = [
  { name: "Executive Overview", href: "/", icon: LayoutDashboard },
  { name: "School 360", href: "/schools", icon: GraduationCap },
  { name: "Welfare & Infrastructure", href: "/welfare", icon: Building2 },
  { name: "Mid-Day Meals", href: "/procurement", icon: Utensils },
  { name: "Intervention Command", href: "/intervention", icon: AlertTriangle },
  { name: "Data Trust & Governance", href: "/quality", icon: ShieldCheck },
  { name: "AI Decision Analyst", href: "/ai-analyst", icon: Bot },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[230px] bg-white border-r border-slate-200 flex flex-col h-screen sticky top-0 select-none z-30 shrink-0">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-100 shrink-0">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-sky-700 flex items-center justify-center text-white font-bold shadow-xs">
            <Layers className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="font-bold text-slate-900 text-sm tracking-tight">
              EDUPULSE AI
            </div>
            <div className="text-[11px] text-slate-500 font-medium">
              Welfare Command Center
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          Decision Intelligence
        </div>
        {navigationItems.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition-colors",
                isActive
                  ? "bg-sky-50 text-sky-800 font-semibold border-l-2 border-sky-600 pl-2"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              )}
            >
              <Icon
                className={cn(
                  "w-4 h-4 shrink-0 transition-colors",
                  isActive ? "text-sky-700" : "text-slate-400"
                )}
              />
              <span className="truncate">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Compact Status Pill */}
      <div className="p-3 border-t border-slate-100 bg-slate-50/70 shrink-0">
        <div className="bg-white rounded-lg p-2.5 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-[10px] text-slate-500 font-medium mb-1">
            <span className="flex items-center gap-1 font-semibold text-slate-700">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Data Trust Index
            </span>
            <span className="text-[9px] font-bold text-emerald-700 bg-emerald-50 px-1 py-0.2 rounded border border-emerald-200">
              Pass
            </span>
          </div>

          <div className="flex items-baseline justify-between mt-1">
            <div className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>94.6 / 100</span>
            </div>
            <div className="text-[10px] text-slate-400 flex items-center gap-1">
              <Database className="w-3 h-3 text-slate-400" />
              <span>Governed Mart</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
