import { LayoutDashboard, Briefcase, Search, Newspaper, Bot } from "lucide-react";
import { Button } from "./ui/button";

interface NavigationProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export function Navigation({ currentPage, onNavigate }: NavigationProps) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "portfolio-builder", label: "Portfolio Builder", icon: Briefcase },
    { id: "stock-explorer", label: "Stock Explorer", icon: Search },
    { id: "news", label: "Market News", icon: Newspaper },
    { id: "ai-assistant", label: "AI Assistant", icon: Bot },
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-[1600px] mx-auto px-6">
        <div className="flex items-center justify-between py-4">
          {/* Logo / Title */}
          <div className="flex-shrink-0">
            <h1 className="text-xl font-semibold text-slate-900">
              AI-Powered Portfolio Optimizer
            </h1>
            <p className="text-xs text-slate-600 mt-0.5">
              Dynamic Portfolio Analysis & Risk Management
            </p>
          </div>

          {/* Navigation */}
          <nav className="flex items-center gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              
              return (
                <Button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  variant={isActive ? "default" : "ghost"}
                  className={`gap-2 ${
                    isActive
                      ? "bg-blue-600 text-white hover:bg-blue-700"
                      : "text-slate-700 hover:text-slate-900 hover:bg-slate-100"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden md:inline">{item.label}</span>
                </Button>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}
