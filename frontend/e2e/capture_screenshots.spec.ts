import { test } from "@playwright/test";
import path from "path";

const ARTIFACT_DIR = "/Users/amitkumar/.gemini/antigravity-ide/brain/067def23-c42c-4080-84a7-6be745ddb17f";

test.describe("Capture Clean White Enterprise UI Screenshots", () => {
  test("Capture all redesigned pages", async ({ page }) => {
    // Set desktop executive briefing viewport
    await page.setViewportSize({ width: 1440, height: 900 });

    // 1. Executive Dashboard
    await page.goto("/");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "executive_dashboard_white.png"), fullPage: false });

    // 2. School Directory
    await page.goto("/schools");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "schools_directory_white.png"), fullPage: false });

    // 3. School 360 Profile
    await page.goto("/schools/SCH0386");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "school_360_white.png"), fullPage: false });

    // 4. Welfare & Infrastructure
    await page.goto("/welfare");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "welfare_infrastructure_white.png"), fullPage: false });

    // 5. Mid-Day Meal Procurement
    await page.goto("/procurement");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "procurement_nutrition_white.png"), fullPage: false });

    // 6. Intervention & Risk
    await page.goto("/intervention");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "intervention_matrix_white.png"), fullPage: false });

    // 7. Data Trust & Quality
    await page.goto("/quality");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "data_trust_governance_white.png"), fullPage: false });

    // 8. AI Analyst Workbench
    await page.goto("/ai-analyst");
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "ai_analyst_workbench_white.png"), fullPage: false });

    // 9. Floating Copilot
    const trigger = page.locator("button[aria-label='Toggle AI Decision Assistant']");
    if (await trigger.isVisible()) {
      await trigger.click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(ARTIFACT_DIR, "ai_copilot_white.png"), fullPage: false });
    }
  });
});
