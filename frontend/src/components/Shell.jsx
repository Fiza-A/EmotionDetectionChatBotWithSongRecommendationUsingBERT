import { Bot, ChartNoAxesColumn, LogOut, MessageCircle, Pencil, Plus, Settings, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { conversationApi } from "../services/api";

const nav = [
  { to: "/", label: "Chat", icon: MessageCircle },
  { to: "/history", label: "Mood", icon: ChartNoAxesColumn },
  { to: "/preferences", label: "Preferences", icon: Settings }
];

export default function Shell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [loadingConversations, setLoadingConversations] = useState(true);

  const refreshConversations = async (preferredActiveId) => {
    setLoadingConversations(true);
    try {
      const { data } = await conversationApi.list();
      setConversations(data);
      if (preferredActiveId) {
        setActiveConversationId(preferredActiveId);
      } else if (!activeConversationId && data.length > 0) {
        setActiveConversationId(data[0].id);
      }
    } finally {
      setLoadingConversations(false);
    }
  };

  useEffect(() => {
    refreshConversations();
  }, []);

  const startNewChat = async () => {
    const { data } = await conversationApi.create();
    setConversations((current) => [data, ...current.filter((item) => item.id !== data.id)]);
    setActiveConversationId(data.id);
    navigate("/");
  };

  const renameConversation = async (conversation, event) => {
    event.stopPropagation();
    const title = window.prompt("Rename conversation", conversation.title);
    if (!title || title.trim() === conversation.title) return;
    const { data } = await conversationApi.rename(conversation.id, title.trim());
    setConversations((current) => current.map((item) => (item.id === data.id ? data : item)));
  };

  const deleteConversation = async (conversation, event) => {
    event.stopPropagation();
    if (!window.confirm(`Delete "${conversation.title}"?`)) return;
    await conversationApi.delete(conversation.id);
    setConversations((current) => {
      const next = current.filter((item) => item.id !== conversation.id);
      if (activeConversationId === conversation.id) {
        setActiveConversationId(next[0]?.id || null);
      }
      return next;
    });
  };

  const handleLogout = () => {
    setConversations([]);
    setActiveConversationId(null);
    logout();
  };

  return (
    <div className="box-border h-screen w-screen overflow-hidden px-4 py-5 sm:px-6 lg:px-8">
      <div className="mx-auto flex h-full min-h-0 max-w-7xl flex-col overflow-hidden rounded-[28px] border border-white/80 bg-white/55 shadow-glow backdrop-blur-xl lg:flex-row">
        <aside className="flex shrink-0 flex-col gap-5 overflow-hidden border-b border-slate-200/80 p-4 lg:h-full lg:w-72 lg:border-b-0 lg:border-r">
          <div className="flex items-center gap-3 px-2">
            <div className="grid h-12 w-12 place-items-center rounded-2xl bg-slate-950 text-white">
              <Bot size={25} />
            </div>
            <div>
              <h1 className="text-lg font-extrabold tracking-tight">MoodMate</h1>
              <p className="text-sm text-slate-500">Emotion-aware picks</p>
            </div>
          </div>
          <button onClick={startNewChat} className="flex w-full items-center justify-center gap-2 rounded-2xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white shadow-lg hover:bg-slate-800">
            <Plus size={18} />
            New Chat
          </button>
          <nav className="grid gap-2">
            {nav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                    isActive ? "bg-slate-950 text-white shadow-lg" : "text-slate-600 hover:bg-white/80 hover:text-slate-950"
                  }`
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="min-h-0 flex-1 overflow-hidden">
            <h3 className="px-2 pb-2 text-xs font-bold uppercase tracking-wide text-slate-500">Recents</h3>
            <div className="flex max-h-full flex-col gap-1 overflow-y-auto pr-1 scrollbar-thin">
              {loadingConversations && <p className="px-2 py-2 text-sm text-slate-500">Loading chats...</p>}
              {!loadingConversations && conversations.length === 0 && <p className="px-2 py-2 text-sm text-slate-500">No recent chats yet</p>}
              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => {
                    setActiveConversationId(conversation.id);
                    navigate("/");
                  }}
                  className={`group flex items-center gap-2 rounded-2xl px-3 py-2 text-left text-sm font-semibold transition ${
                    activeConversationId === conversation.id
                      ? "bg-slate-950 text-white shadow-lg"
                      : "text-slate-600 hover:bg-white/80 hover:text-slate-950"
                  }`}
                >
                  <span className="min-w-0 flex-1 truncate">{conversation.title}</span>
                  <span className="hidden shrink-0 gap-1 group-hover:flex">
                    <span onClick={(event) => renameConversation(conversation, event)} className="rounded-lg p-1 hover:bg-white/30">
                      <Pencil size={13} />
                    </span>
                    <span onClick={(event) => deleteConversation(conversation, event)} className="rounded-lg p-1 hover:bg-white/30">
                      <Trash2 size={13} />
                    </span>
                  </span>
                </button>
              ))}
            </div>
          </div>
          <div className="mt-auto rounded-2xl bg-white/70 p-4">
            <p className="font-semibold text-slate-900">{user?.username}</p>
            <p className="truncate text-sm text-slate-500">{user?.email}</p>
            <button onClick={handleLogout} className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700 hover:bg-rose-100">
              <LogOut size={16} /> Logout
            </button>
          </div>
          <p className="px-2 text-xs leading-5 text-slate-500">MoodMate is not a therapist or medical tool. If you feel unsafe, contact trusted support or emergency services.</p>
        </aside>
        <main className="min-h-0 min-w-0 flex-1 overflow-hidden">
          <Outlet context={{ conversations, activeConversationId, setActiveConversationId, refreshConversations, setConversations }} />
        </main>
      </div>
    </div>
  );
}
