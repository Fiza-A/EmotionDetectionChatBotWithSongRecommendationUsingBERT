import { AnimatePresence, motion } from "framer-motion";
import { SendHorizontal, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import RecommendationCard from "../components/RecommendationCard";
import TypingIndicator from "../components/TypingIndicator";
import { chatApi } from "../services/api";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [latest, setLatest] = useState(null);
  const bottom = useRef(null);

  useEffect(() => {
    chatApi.history().then(({ data }) => setMessages(data)).catch(() => setMessages([]));
  }, []);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const submit = async (event) => {
    event.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError("");
    const text = input;
    setInput("");
    try {
      const { data } = await chatApi.send(text);
      setMessages((current) => [...current, data.user_message, data.bot_message]);
      setLatest(data);
    } catch (err) {
      setError(err.response?.data?.detail || "I could not send that message.");
      setInput(text);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid h-full grid-rows-[auto_1fr_auto]">
      <header className="border-b border-slate-200/80 p-5 sm:p-7">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-teal-50 text-teal-700"><Sparkles /></div>
          <div>
            <h2 className="text-2xl font-extrabold text-slate-950">Emotion Chat</h2>
            <p className="text-sm text-slate-500">Share a thought. The bot detects a primary mood and keeps recommendations light-aware.</p>
          </div>
        </div>
      </header>
      <section className="overflow-y-auto p-4 scrollbar-thin sm:p-7">
        {messages.length === 0 && (
          <div className="mx-auto mt-16 max-w-xl text-center">
            <h3 className="text-3xl font-extrabold text-slate-950">What’s the weather inside?</h3>
            <p className="mt-3 leading-7 text-slate-500">Try “I am not feeling good today” or “I’m excited for my trip” and the app will store your mood history.</p>
          </div>
        )}
        <div className="mx-auto flex max-w-4xl flex-col gap-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div key={message.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[82%] rounded-3xl px-5 py-3 shadow-sm ${message.sender === "user" ? "bg-slate-950 text-white" : "bg-white text-slate-700"}`}>
                  <p className="leading-7">{message.message_text}</p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {loading && <TypingIndicator />}
          {latest?.recommendations?.length > 0 && (
            <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {latest.recommendations.map((item) => (
                <RecommendationCard key={item.id} item={item} emotion={latest.detected_emotion} />
              ))}
            </div>
          )}
          <div ref={bottom} />
        </div>
      </section>
      <footer className="border-t border-slate-200/80 p-4 sm:p-5">
        {error && <p className="mx-auto mb-3 max-w-4xl rounded-2xl bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{error}</p>}
        <form onSubmit={submit} className="mx-auto flex max-w-4xl gap-3">
          <input className="min-w-0 flex-1 rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 outline-none focus:border-teal-500" placeholder="Type your message..." value={input} onChange={(e) => setInput(e.target.value)} />
          <button disabled={loading} className="grid h-12 w-12 place-items-center rounded-2xl bg-slate-950 text-white shadow-lg hover:bg-slate-800 disabled:opacity-50">
            <SendHorizontal size={20} />
          </button>
        </form>
      </footer>
    </div>
  );
}
