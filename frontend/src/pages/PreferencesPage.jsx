import { useState } from "react";
import LanguageSelector from "../components/LanguageSelector";
import { useAuth } from "../hooks/useAuth";
import { userApi } from "../services/api";

export default function PreferencesPage() {
  const { user, setUser } = useAuth();
  const [languages, setLanguages] = useState(user?.preferences?.preferred_languages || ["English"]);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  const save = async () => {
    setError("");
    setSaved(false);
    try {
      const { data } = await userApi.updatePreferences(languages);
      setUser({ ...user, preferences: data });
      setSaved(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not update preferences.");
    }
  };

  return (
    <div className="p-5 sm:p-8">
      <div className="max-w-3xl">
        <h2 className="text-3xl font-extrabold text-slate-950">Preferences</h2>
        <p className="mt-2 text-slate-500">Recommendations prioritize your selected languages, then fall back gracefully when more variety is needed.</p>
        <div className="mt-8 rounded-3xl bg-white/75 p-6 shadow-sm">
          <h3 className="mb-4 text-lg font-bold">Preferred languages</h3>
          <LanguageSelector selected={languages} onChange={setLanguages} />
          {error && <p className="mt-4 rounded-2xl bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{error}</p>}
          {saved && <p className="mt-4 rounded-2xl bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-700">Preferences updated.</p>}
          <button onClick={save} className="mt-6 rounded-2xl bg-slate-950 px-5 py-3 font-bold text-white hover:bg-slate-800">Save preferences</button>
        </div>
      </div>
    </div>
  );
}
