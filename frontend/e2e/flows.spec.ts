import { test, expect } from "@playwright/test";

test.describe("EduPulse AI Web Platform Critical User Journeys", () => {
  test("1. Executive Overview loads with KPIs and alerts", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/EduPulse AI/i);

    // Verify Brand Sidebar (scoped to aside to avoid strict mode collision with floating chat button)
    await expect(page.locator("aside").getByText("EDUPULSE AI")).toBeVisible();
    await expect(page.getByText("Welfare Command Center")).toBeVisible();

    // Verify KPI Cards
    await expect(page.getByText("Schools Monitored")).toBeVisible();
    await expect(page.getByText("Average Attendance")).toBeVisible();
    await expect(page.getByText("Academic FLN Score", { exact: true })).toBeVisible();
    await expect(page.getByText("Priority Schools", { exact: true })).toBeVisible();

    // Verify Trust Pill
    await expect(page.getByText("94.6 / 100").first()).toBeVisible();
  });

  test("2. Navigation through all consulting views", async ({ page }) => {
    // School Directory
    await page.goto("/schools");
    await expect(page.getByText("School Directory & Search")).toBeVisible();

    // Welfare & Infrastructure
    await page.goto("/welfare");
    await expect(page.getByText("Welfare & Infrastructure Intelligence")).toBeVisible();
    await expect(page.getByText("Competition Benchmark: Electricity Availability vs. FLN Test Scores")).toBeVisible();

    // Mid-Day Meals Procurement
    await page.goto("/procurement");
    await expect(page.getByText("Mid-Day Meal Nutritional Welfare & Procurement")).toBeVisible();
    await expect(page.getByText("Peer Benchmark Exceptions")).toBeVisible();

    // Intervention Command Center
    await page.goto("/intervention");
    await expect(page.getByText("Intervention & Risk Command Center")).toBeVisible();
    await expect(page.getByText("Risk Severity vs. Intervention Priority Matrix")).toBeVisible();

    // Data Trust & Governance
    await page.goto("/quality");
    await expect(page.getByText("Data Trust & Governance Center")).toBeVisible();
    await expect(page.getByText("Ten Governed Data Quality Gates (100% Pass)")).toBeVisible();

    // AI Analyst Workbench
    await page.goto("/ai-analyst");
    await expect(page.getByText("AI Analyst — Decision Intelligence Workbench")).toBeVisible();
    await expect(page.getByText("Enterprise Autonomous Education Analyst")).toBeVisible();
  });

  test("3. School 360 Profile drilldown", async ({ page }) => {
    await page.goto("/schools/SCH0386");
    // Should render school profile elements
    await expect(page.getByText("SCH0386").first()).toBeVisible();
    await expect(page.getByText("Physical Infrastructure Amenities Checklist")).toBeVisible();
    await expect(page.getByText("Recommended Operational Policy Action:")).toBeVisible();
  });

  test("4. AI Analyst interactive prompt execution", async ({ page }) => {
    await page.goto("/ai-analyst");
    await expect(page.getByText("AI Analyst — Decision Intelligence Workbench")).toBeVisible();
    await page.getByText("Regional Attendance & Academic Disparity").click();

    // Expect response container to appear
    await expect(page.getByText("Evidence-Grounded Policy Finding")).toBeVisible({ timeout: 15000 });
    await expect(page.getByText("Grounding Integrity Audit")).toBeVisible();
  });
});
