import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import LanguageSelector from "../components/LanguageSelector";
import { useAuth } from "../hooks/useAuth";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "", confirm: "", preferred_languages: ["English", "Hindi"] });
  const [error, setError] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    if (form.password !== form.confirm) return setError("Passwords do not match.");
    try {
      await register({
        username: form.username,
        email: form.email,
        password: form.password,
        preferred_languages: form.preferred_languages
      });
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed.");
    }
  };

  return (
    <AuthLayout title="Build a recommendation space around your mood." subtitle="Choose your languages first, then the chatbot will prioritize them while keeping recommendations uplifting.">
      <form onSubmit={submit} className="mx-auto flex max-w-md flex-col justify-center gap-4">
        <h2 className="text-3xl font-extrabold text-slate-950">Register</h2>
        {error && <p className="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{error}</p>}
        <input className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 outline-none focus:border-teal-500" placeholder="Username" required minLength={3} value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <input className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 outline-none focus:border-teal-500" placeholder="Email" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 outline-none focus:border-teal-500" placeholder="Password" type="password" required minLength={8} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <input className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 outline-none focus:border-teal-500" placeholder="Confirm password" type="password" required value={form.confirm} onChange={(e) => setForm({ ...form, confirm: e.target.value })} />
        <LanguageSelector selected={form.preferred_languages} onChange={(preferred_languages) => setForm({ ...form, preferred_languages })} />
        <button className="rounded-2xl bg-slate-950 px-5 py-3 font-bold text-white shadow-lg hover:bg-slate-800">Create account</button>
        <p className="text-center text-sm text-slate-500">Already registered? <Link className="font-bold text-teal-700" to="/login">Login</Link></p>
      </form>
    </AuthLayout>
  );
}
