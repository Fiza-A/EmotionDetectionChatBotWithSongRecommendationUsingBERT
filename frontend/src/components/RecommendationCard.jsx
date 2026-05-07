import { Film, Music2, ThumbsDown, ThumbsUp } from "lucide-react";
import { recommendationApi } from "../services/api";

export default function RecommendationCard({ item, emotion, onFeedback }) {
  const Icon = item.type === "song" ? Music2 : Film;
  const sendFeedback = async (feedback) => {
    await recommendationApi.feedback({ recommendation_id: item.id, detected_emotion: emotion, feedback });
    onFeedback?.(item.id, feedback);
  };
  return (
    <article className="soft-panel rounded-2xl p-4 transition hover:-translate-y-0.5 hover:shadow-lg">
      <div className="mb-3 flex items-center justify-between gap-2">
        {item.image_url || item.album_art ? (
          <img src={item.image_url || item.album_art} alt="" className="h-12 w-12 rounded-xl object-cover shadow-sm" />
        ) : (
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-teal-50 text-teal-700">
            <Icon size={20} />
          </span>
        )}
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">{item.language}</span>
      </div>
      <h3 className="line-clamp-2 text-base font-extrabold text-slate-950">{item.title}</h3>
      <p className="mt-1 text-sm text-slate-500">{item.creator || item.genre} {item.year ? `• ${item.year}` : ""}</p>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {item.mood_tags.slice(0, 3).map((tag) => (
          <span key={tag} className="rounded-full bg-pink-50 px-2.5 py-1 text-xs font-semibold text-pink-700">{tag}</span>
        ))}
      </div>
      <div className="mt-4 flex items-center gap-2">
        {item.preview_url && (
          <audio controls src={item.preview_url} className="h-9 min-w-0 flex-1" />
        )}
        {(item.external_url || item.link) && (
          <a className={`${item.preview_url ? "" : "mr-auto"} rounded-xl bg-slate-950 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800`} href={item.external_url || item.link} target="_blank" rel="noreferrer">
            Open
          </a>
        )}
        <button aria-label="Like recommendation" onClick={() => sendFeedback("like")} className="rounded-xl bg-emerald-50 p-2 text-emerald-700 hover:bg-emerald-100">
          <ThumbsUp size={17} />
        </button>
        <button aria-label="Dislike recommendation" onClick={() => sendFeedback("dislike")} className="rounded-xl bg-rose-50 p-2 text-rose-700 hover:bg-rose-100">
          <ThumbsDown size={17} />
        </button>
      </div>
    </article>
  );
}
