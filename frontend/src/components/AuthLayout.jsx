import { Bot } from "lucide-react";

export default function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="grid min-h-screen place-items-center px-4 py-10">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-[32px] border border-white/80 bg-white/60 shadow-glow backdrop-blur-xl md:grid-cols-[0.95fr_1.05fr]">
        <section className="relative flex min-h-[560px] flex-col justify-between overflow-hidden bg-slate-950 p-8 text-white">
          <img
            src="https://images.unsplash.com/photo-1493246507139-91e8fad9978e?auto=format&fit=crop&w=1200&q=80"
            alt=""
            className="absolute inset-0 h-full w-full object-cover opacity-45"
          />
          <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900/70 to-teal-950/40" />
          <div className="relative flex items-center gap-3">
            <div className="grid h-12 w-12 place-items-center rounded-2xl bg-white text-slate-950">
              <Bot />
            </div>
            <span className="text-xl font-extrabold">MoodMate</span>
          </div>
          <div className="relative max-w-sm">
            <h1 className="text-4xl font-extrabold leading-tight md:text-5xl">{title}</h1>
            <p className="mt-4 text-base leading-7 text-white/78">{subtitle}</p>
          </div>
        </section>
        <section className="p-6 sm:p-10">{children}</section>
      </div>
    </div>
  );
}
