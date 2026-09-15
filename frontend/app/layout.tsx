import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/providers";
import { FilterProvider } from "@/components/filters/filter-context";
import { Sidebar } from "@/components/layout/sidebar";
import { GlobalAIChatbot } from "@/components/chatbot/global-chatbot";

export const metadata: Metadata = {
  title: "EduPulse AI — Education Welfare Command Center",
  description: "Clean. Connect. Detect. Explain. Act. Enterprise decision intelligence platform for Track 4: Education & EdTech.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-[#F8FAFC] text-slate-900">
      <body className="h-full flex min-h-screen bg-[#F8FAFC] text-slate-900 antialiased">
        <Providers>
          <FilterProvider>
            <div className="flex w-full min-h-screen">
              <Sidebar />
              <main className="flex-1 flex flex-col min-w-0 bg-[#F8FAFC]">
                {children}
              </main>
              <GlobalAIChatbot />
            </div>
          </FilterProvider>
        </Providers>
      </body>
    </html>
  );
}
