import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricCard } from "@/components/kpi/metric-card";
import { AlertBanner } from "@/components/kpi/alert-banner";
import { formatNumber, formatPercent, formatINR, formatKG, formatGap } from "@/lib/utils/formatters";
import type { DynamicAlert, MetricContext } from "@/lib/types";

describe("Formatters", () => {
  it("formats numbers with Indian locale correctly", () => {
    expect(formatNumber(1250)).toBe("1,250");
    expect(formatNumber(1250.456, 1)).toBe("1,250.5");
    expect(formatNumber(null)).toBe("-");
    expect(formatNumber(undefined)).toBe("-");
  });

  it("formats percentages correctly", () => {
    expect(formatPercent(78.54)).toBe("78.5%");
    expect(formatPercent(100, 0)).toBe("100%");
    expect(formatPercent(null)).toBe("-");
  });

  it("formats INR currency in lakhs and crores", () => {
    expect(formatINR(500)).toBe("₹500");
    expect(formatINR(25000)).toBe("₹25.0k");
    expect(formatINR(550000)).toBe("₹5.50 Lakh");
    expect(formatINR(25000000)).toBe("₹2.50 Cr");
    expect(formatINR(null)).toBe("₹0");
  });

  it("formats KG and MT quantities", () => {
    expect(formatKG(250)).toBe("250 kg");
    expect(formatKG(5400)).toBe("5.4 MT");
    expect(formatKG(null)).toBe("0 kg");
  });

  it("formats benchmark gaps with signs", () => {
    expect(formatGap(3.5)).toBe("+3.5");
    expect(formatGap(-2.1)).toBe("-2.1");
    expect(formatGap(0)).toBe("0.0");
    expect(formatGap(null)).toBe("0.0");
  });
});

describe("MetricCard Component", () => {
  it("renders metric context with title, coverage, and benchmark delta", () => {
    const ctx: MetricContext = {
      value: 78.4,
      unit: "%",
      metric: "attendance_rate",
      coverage_pct: 94.2,
      source: "DuckDB Mart",
      method: "Weighted Average",
      benchmark: 75.0,
    };

    render(<MetricCard title="Average Attendance" metricCtx={ctx} />);

    expect(screen.getByText("Average Attendance")).toBeInTheDocument();
    expect(screen.getByText("78.4%")).toBeInTheDocument();
    expect(screen.getByText("94.2% coverage")).toBeInTheDocument();
    expect(screen.getByText("+3.4 pts vs BM")).toBeInTheDocument();
    expect(screen.getByText("DuckDB Mart")).toBeInTheDocument();
  });

  it("renders custom value without metric context", () => {
    render(<MetricCard title="Total Schools" customValue={600} subtitle="6 districts active" />);

    expect(screen.getByText("Total Schools")).toBeInTheDocument();
    expect(screen.getByText("600")).toBeInTheDocument();
    expect(screen.getByText("6 districts active")).toBeInTheDocument();
  });
});

describe("AlertBanner Component", () => {
  it("renders dynamic alert strip with evidence, interpretation, and limitation", () => {
    const alerts: DynamicAlert[] = [
      {
        title: "Attendance Deficit in Vadodara",
        finding: "Attendance dropped below 70% across 14 rural schools.",
        evidence: "14 schools observed with <70% weighted 30-day rate.",
        interpretation: "Correlates with harvesting season and transit constraints.",
        limitation: "Observational data; local transport verification needed.",
        level: "warning",
      },
    ];

    render(<AlertBanner alerts={alerts} />);

    expect(screen.getByText("Attendance Deficit in Vadodara")).toBeInTheDocument();
    expect(screen.getByText("Attendance dropped below 70% across 14 rural schools.")).toBeInTheDocument();
    expect(screen.getByText(/14 schools observed with <70%/)).toBeInTheDocument();
    expect(screen.getByText(/Correlates with harvesting season/)).toBeInTheDocument();
    expect(screen.getByText(/Observational data; local transport verification needed./)).toBeInTheDocument();
  });

  it("returns null when alerts list is empty", () => {
    const { container } = render(<AlertBanner alerts={[]} />);
    expect(container.firstChild).toBeNull();
  });
});
