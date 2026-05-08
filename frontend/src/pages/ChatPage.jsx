import { AnimatePresence, motion } from "framer-motion";
import { SendHorizontal, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useOutletContext } from "react-router-dom";
import RecommendationCard from "../components/RecommendationCard";
import TypingIndicator from "../components/TypingIndicator";
import { chatApi, conversationApi } from "../services/api";

function recommendationItems(recommendations) {
  if (Array.isArray(recommendations)) return recommendations;
  if (recommendations && typeof recommendations === "object") {
    return [...(recommendations.songs || []), ...(recommendations.movies || [])];
  }
  return [];
}

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [error, setError] = useState("");
  const { activeConversationId, setActiveConversationId, refreshConversations } = useOutletContext();
  const messagesScroll = useRef(null);
  const bottom = useRef(null);

  useEffect(() => {
    if (!activeConversationId) {
      setMessages([]);
      return;
    }
    setLoadingMessages(true);
    conversationApi
      .detail(activeConversationId)
      .then(({ data }) => setMessages(data.messages || []))
      .catch(() => setMessages([]))
      .finally(() => setLoadingMessages(false));
  }, [activeConversationId]);

  useEffect(() => {
    if (messagesScroll.current) {
      messagesScroll.current.scrollTo({
        top: messagesScroll.current.scrollHeight,
        behavior: "smooth"
      });
    } else {
      bottom.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading]);

  const submit = async (event) => {
    event.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError("");
    const text = input;
    setInput("");
    try {
      const { data } = await chatApi.send(text, activeConversationId);
      if (!activeConversationId) {
        setActiveConversationId(data.conversation_id);
      }
      setMessages((current) => [...current, data.user_message, data.bot_message]);
      refreshConversations(data.conversation_id);
    } catch (err) {
      setError(err.response?.data?.detail || "I could not send that message.");
      setInput(text);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden">
      <header className="shrink-0 border-b border-slate-200/80 p-5 sm:p-7">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-teal-50 text-teal-700"><Sparkles /></div>
          <div>
            <h2 className="text-2xl font-extrabold text-slate-950">Emotion Chat</h2>
            <p className="text-sm text-slate-500">Share a thought. The bot detects a primary mood and keeps recommendations light-aware.</p>
          </div>
        </div>
      </header>
      <section ref={messagesScroll} className="min-h-0 flex-1 overflow-y-auto p-4 pb-8 scrollbar-thin sm:p-7 sm:pb-10">
        {!loadingMessages && messages.length === 0 && (
          <div className="mx-auto mt-16 max-w-xl text-center">
            <h3 className="text-3xl font-extrabold text-slate-950">{activeConversationId ? "This conversation is empty" : "Start a new conversation"}</h3>
            <p className="mt-3 leading-7 text-slate-500">Try "I am not feeling good today" or "I'm excited for my trip" and the app will store your mood history.</p>
          </div>
        )}
        <div className="mx-auto flex max-w-4xl flex-col gap-4">
          {loadingMessages && <TypingIndicator />}
          <AnimatePresence>
            {messages.map((message) => {
              const items = recommendationItems(message.recommendations);
              return (
                <motion.div key={message.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
                  <div className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[82%] rounded-3xl px-5 py-3 shadow-sm ${message.sender === "user" ? "bg-slate-950 text-white" : "bg-white text-slate-700"}`}>
                      <p className="leading-7">{message.message_text}</p>
                    </div>
                  </div>
                  {items.length > 0 && (
                    <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                      {items.map((item) => (
                        <RecommendationCard key={`${message.id}-${item.id}`} item={item} emotion={message.detected_emotion} />
                      ))}
                    </div>
                  )}
                  {message.recommendation_message && (
                    <p className="mt-3 rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-600 shadow-sm">
                      {message.recommendation_message}
                    </p>
                  )}
                </motion.div>
              );
            })}
          </AnimatePresence>
          {loading && <TypingIndicator />}
          <div ref={bottom} />
        </div>
      </section>
      <footer className="shrink-0 border-t border-slate-200/80 p-4 sm:p-5">
        {error && <p className="mx-auto mb-3 max-w-4xl rounded-2xl bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{error}</p>}
        <form onSubmit={submit} className="mx-auto flex max-w-4xl gap-3">
          <input className="min-w-0 flex-1 rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 outline-none focus:border-teal-500" placeholder="Type your message..." value={input} onChange={(e) => setInput(e.target.value)} />
          <button disabled={loading || !input.trim()} className="grid h-12 w-12 place-items-center rounded-2xl bg-slate-950 text-white shadow-lg hover:bg-slate-800 disabled:opacity-50">
            <SendHorizontal size={20} />
          </button>
        </form>
      </footer>
    </div>
  );
}
