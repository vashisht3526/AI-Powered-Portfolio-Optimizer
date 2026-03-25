import { useState } from "react";
import { Navigation } from "./components/navigation";
import { DashboardPage } from "./pages/dashboard-page";
import { PortfolioBuilderPage } from "./pages/portfolio-builder-page";
import { StockExplorerPage } from "./pages/stock-explorer-page";
import { MarketNewsPage } from "./pages/market-news-page";
import { AIAssistantPage } from "./pages/ai-assistant-page";

type PageType = "dashboard" | "portfolio-builder" | "stock-explorer" | "news" | "ai-assistant";

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageType>("dashboard");

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <DashboardPage />;
      case "portfolio-builder":
        return <PortfolioBuilderPage />;
      case "stock-explorer":
        return <StockExplorerPage />;
      case "news":
        return <MarketNewsPage />;
      case "ai-assistant":
        return <AIAssistantPage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Navigation currentPage={currentPage} onNavigate={(page) => {
        console.log("Navigating to:", page);
        setCurrentPage(page as PageType)
      }} />
      
      <main className="pb-12">
        {renderPage()}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200">
        <div className="max-w-[1600px] mx-auto px-6 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-slate-600">
              <span className="font-semibold">Academic Project:</span> Mini-Project on AI-Powered Portfolio Optimization
            </p>
            <p className="text-xs text-slate-500">
              This system is for educational and decision support purposes only. Not intended for
              live trading or financial advice.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
