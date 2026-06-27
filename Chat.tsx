/**
 * MifugoIQ Chat Component
 * Paste this into Lovable as: src/components/Chat.tsx
 *
 * Connects to your FastAPI backend via VITE_API_URL.
 * Supports English and Kiswahili input.
 */
import { useState, useRef, useEffect } from "react";
import { askMifugoIQ, ChatResponse } from "../services/mifugoiq";

interface Message {
  role: "user" | "assistant";
  content: string;
  intent?: string;
  source?: string;
}

const SUGGESTED = [
  "What is the price of a Boran steer in Kajiado this month?",
  "Ni bei gani ya ng'ombe wa Boran huko Kajiado?",
  "Where is the best market for my 15 Boran steers from Kajiado?",
  "Which Halal-certified slaughterhouses are near Machakos?",
  "Value 15 Boran steers, 2-3 years, in Kajiado as collateral",
  "What would feed cost for finishing 20 steers over 90 days?",
];

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Karibu! / Welcome to MifugoIQ 🐄\n\nAsk me about cattle prices, slaughterhouses, feed costs, or livestock collateral valuations — in English or Kiswahili.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (query: string) => {
    if (!query.trim() || loading) return;
    const userMsg: Message = { role: "user", content: query };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res: ChatResponse = await askMifugoIQ(query);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.answer,
          intent: res.intent,
          source: res.query_description,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "⚠️ Samahani — unable to reach the MifugoIQ server. Please check your connection and try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-2xl mx-auto">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-green-700 text-white"
                  : "bg-gray-100 text-gray-900 border border-gray-200"
              }`}
            >
              {msg.content}
              {msg.intent && (
                <div className="mt-2 text-xs text-gray-400">
                  [{msg.intent}] · {msg.source}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 border border-gray-200 rounded-2xl px-4 py-3 text-sm text-gray-500">
              <span className="animate-pulse">MifugoIQ inafikiria… / Thinking…</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggested queries — show only when no user messages yet */}
      {messages.length === 1 && (
        <div className="px-4 pb-2">
          <p className="text-xs text-gray-400 mb-2">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED.map((s, i) => (
              <button
                key={i}
                onClick={() => send(s)}
                className="text-xs bg-green-50 border border-green-200 text-green-800 rounded-full px-3 py-1 hover:bg-green-100 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send(input)}
            placeholder="Ask in English au Kiswahili…"
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            disabled={loading}
          />
          <button
            onClick={() => send(input)}
            disabled={loading || !input.trim()}
            className="bg-green-700 text-white rounded-xl px-4 py-2 text-sm font-medium hover:bg-green-800 disabled:opacity-40 transition-colors"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-1 text-center">
          Prices sourced from NDMA, KNBS, DVS bulletins · Every figure is cited
        </p>
      </div>
    </div>
  );
}
