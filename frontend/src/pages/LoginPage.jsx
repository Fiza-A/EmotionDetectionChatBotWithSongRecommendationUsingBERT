import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import { useAuth } from "../hooks/useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await login(form);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check your details.");
    }
  };

  return (
    <AuthLayout title="Welcome back to calmer recommendations." subtitle="Sign in, tell the bot what is on your mind, and get mood-aware music and movie picks.">
      <form onSubmit={submit} className="mx-auto flex h-full max-w-md flex-col justify-center gap-5">
        <div>
          <h2 className="text-3xl font-extrabold text-slate-950">Login</h2>
          <p className="mt-2 text-slate-500">Your mood history and language preferences stay with your account.</p>
        </div>
        {error && <p className="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{error}</p>}
        <input className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 outline-none focus:border-teal-500" placeholder="Email" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 outline-none focus:border-teal-500" placeholder="Password" type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <button className="rounded-2xl bg-slate-950 px-5 py-3 font-bold text-white shadow-lg hover:bg-slate-800">Login</button>
        <p className="text-center text-sm text-slate-500">New here? <Link className="font-bold text-teal-700" to="/register">Create an account</Link></p>
      </form>
    </AuthLayout>
  );
}
