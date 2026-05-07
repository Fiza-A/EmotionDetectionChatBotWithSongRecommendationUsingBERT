export const LANGUAGES = ["English", "Hindi", "Tamil", "Telugu", "Malayalam", "Kannada", "Bengali", "Marathi", "Punjabi", "Gujarati"];

export default function LanguageSelector({ selected, onChange }) {
  const toggle = (language) => {
    if (selected.includes(language)) {
      onChange(selected.filter((item) => item !== language));
    } else {
      onChange([...selected, language]);
    }
  };
  return (
    <div className="flex flex-wrap gap-2">
      {LANGUAGES.map((language) => (
        <button
          type="button"
          key={language}
          onClick={() => toggle(language)}
          className={`rounded-full border px-3 py-2 text-sm font-semibold transition ${
            selected.includes(language)
              ? "border-slate-950 bg-slate-950 text-white"
              : "border-slate-200 bg-white/80 text-slate-600 hover:border-teal-400"
          }`}
        >
          {language}
        </button>
      ))}
    </div>
  );
}
