import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { ScrollArea } from "../components/ui/scroll-area";
import { Badge } from "../components/ui/badge";
import { Bot, User, Send, Sparkles, MessageSquare, AlertCircle } from "lucide-react";
import { sendAiMessage } from "../../api/ai";
import { getMarketNews } from "../../api/news";
import { getPortfolioMetrics } from "../../api/portfolio";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

const suggestedQuestions = [
  "What is my portfolio's current risk level?",
  "How does recent market news affect my holdings?",
  "Explain the maximum drawdown in my portfolio",
  "Should I be concerned about portfolio diversification?",
  "What does my Sharpe ratio indicate?",
  "How correlated are my tech stocks?",
];

export function AIAssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm your AI Portfolio Analysis Assistant. I'm here to help you understand your portfolio's risk profile, interpret market news, analyze diversification, and explain key financial metrics. How can I assist you today?",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const metrics = await getPortfolioMetrics({ mode: "system" });
      let news = [];
      try {
        const newsResponse = await getMarketNews();
        news = newsResponse.news;
      } catch (error) {
        news = [];
      }
      const response = await sendAiMessage({
        question: userMessage.content,
        portfolio: metrics.metrics,
        news,
      });
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    } catch (error) {
      console.error(error);
      const message =
        error instanceof Error ? error.message : "Sorry, I couldn't reach the AI service.";
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: message,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setInputValue(question);
  };

  return (
    <div className="max-w-[1200px] mx-auto px-6 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-slate-900 flex items-center gap-2">
          <Bot className="h-7 w-7 text-blue-600" />
          AI Portfolio Assistant
        </h2>
        <p className="text-sm text-slate-600 mt-1">
          Get intelligent insights about your portfolio, risk analysis, and market context
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Interface - Main Column */}
        <div className="lg:col-span-2">
          <Card className="border-slate-200 h-[calc(100vh-16rem)] flex flex-col">
            <CardHeader className="border-b border-slate-200 flex-shrink-0">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Bot className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <CardTitle>Conversation</CardTitle>
                  <CardDescription>Ask questions about your portfolio and market insights</CardDescription>
                </div>
              </div>
            </CardHeader>

            {/* Messages */}
            <ScrollArea className="flex-1 p-6">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {message.role === "assistant" && (
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <Bot className="h-4 w-4 text-blue-600" />
                      </div>
                    )}
                    <div
                      className={`max-w-[85%] rounded-lg px-4 py-3 ${
                        message.role === "user"
                          ? "bg-blue-600 text-white"
                          : "bg-slate-100 text-slate-900"
                      }`}
                    >
                      <p className="text-sm leading-relaxed whitespace-pre-line">{message.content}</p>
                      <p
                        className={`text-xs mt-2 ${
                          message.role === "user" ? "text-blue-100" : "text-slate-500"
                        }`}
                      >
                        {new Date(message.timestamp).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                    {message.role === "user" && (
                      <div className="flex-shrink-0 w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center">
                        <User className="h-4 w-4 text-slate-600" />
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="flex gap-3 justify-start">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <Bot className="h-4 w-4 text-blue-600" />
                    </div>
                    <div className="max-w-[85%] rounded-lg px-4 py-3 bg-slate-100 text-slate-900">
                      <p className="text-sm leading-relaxed">Analyzing your portfolio...</p>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Input */}
            <div className="p-4 border-t border-slate-200 flex-shrink-0">
              <div className="flex gap-2">
                <Input
                  placeholder="Ask about your portfolio, risk metrics, or market insights..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleSendMessage();
                  }}
                  className="flex-1"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar - Suggestions & Info */}
        <div className="lg:col-span-1 space-y-6">
          {/* Suggested Questions */}
          <Card className="border-slate-200">
            <CardHeader>
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-slate-600" />
                <CardTitle className="text-lg">Suggested Questions</CardTitle>
              </div>
              <CardDescription>Click to quickly ask common questions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {suggestedQuestions.map((question, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="w-full justify-start text-left h-auto py-3 px-4 hover:bg-blue-50 hover:border-blue-300"
                    onClick={() => handleSuggestedQuestion(question)}
                  >
                    <Sparkles className="h-4 w-4 mr-2 text-blue-600 flex-shrink-0" />
                    <span className="text-sm">{question}</span>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Capabilities */}
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle className="text-lg">AI Capabilities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-start gap-2">
                  <Badge className="bg-blue-100 text-blue-700 border-blue-200 mt-0.5">
                    Risk Analysis
                  </Badge>
                  <p className="text-xs text-slate-600">
                    Interpret volatility, Sharpe ratio, and drawdowns
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200 mt-0.5">
                    News Context
                  </Badge>
                  <p className="text-xs text-slate-600">
                    Explain market news impact on holdings
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <Badge className="bg-amber-100 text-amber-700 border-amber-200 mt-0.5">
                    Diversification
                  </Badge>
                  <p className="text-xs text-slate-600">
                    Assess correlation and portfolio balance
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <Badge className="bg-purple-100 text-purple-700 border-purple-200 mt-0.5">
                    Strategy Guidance
                  </Badge>
                  <p className="text-xs text-slate-600">
                    Suggest optimization and risk management
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Disclaimer */}
          <Card className="border-amber-200 bg-amber-50">
            <CardContent className="p-4">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-amber-900 mb-1">
                    Educational Purpose Only
                  </p>
                  <p className="text-xs text-amber-800 leading-relaxed">
                    This AI assistant provides educational analysis and insights. It is not a
                    substitute for professional financial advice. Always consult with qualified
                    advisors before making investment decisions.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
