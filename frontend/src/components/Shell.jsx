import { Bot, ChartNoAxesColumn, LogOut, MessageCircle, Settings } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const nav = [
  { to: "/", label: "Chat", icon: MessageCircle },
  { to: "/history", label: "Mood", icon: ChartNoAxesColumn },
  { to: "/preferences", label: "Preferences", icon: Settings }
];

export default function Shell() {
  const { user, logout } = useAuth();
  return (
    <div className="min-h-screen px-4 py-5 sm:px-6 lg:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-2.5rem)] max-w-7xl flex-col overflow-hidden rounded-[28px] border border-white/80 bg-white/55 shadow-glow backdrop-blur-xl lg:flex-row">
        <aside className="flex flex-col gap-5 border-b border-slate-200/80 p-4 lg:w-72 lg:border-b-0 lg:border-r">
          <div className="flex items-center gap-3 px-2">
            <div className="grid h-12 w-12 place-items-center rounded-2xl bg-slate-950 text-white">
              <Bot size={25} />
            </div>
            <div>
              <h1 className="text-lg font-extrabold tracking-tight">MoodMate</h1>
              <p className="text-sm text-slate-500">Emotion-aware picks</p>
            </div>
          </div>
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
          <div className="mt-auto rounded-2xl bg-white/70 p-4">
            <p className="font-semibold text-slate-900">{user?.username}</p>
            <p className="truncate text-sm text-slate-500">{user?.email}</p>
            <button onClick={logout} className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700 hover:bg-rose-100">
              <LogOut size={16} /> Logout
            </button>
          </div>
          <p className="px-2 text-xs leading-5 text-slate-500">MoodMate is not a therapist or medical tool. If you feel unsafe, contact trusted support or emergency services.</p>
        </aside>
        <main className="flex-1 overflow-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
