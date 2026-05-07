import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { chatApi } from "../services/api";

export default function HistoryPage() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    chatApi.moodHistory().then(({ data }) => setHistory(data)).catch(() => setHistory([]));
  }, []);

  const frequency = useMemo(() => {
    const counts = history.reduce((acc, item) => ({ ...acc, [item.emotion]: (acc[item.emotion] || 0) + 1 }), {});
    return Object.entries(counts).map(([emotion, count]) => ({ emotion, count }));
  }, [history]);

  const trend = history.slice(-20).map((item, index) => ({
    index: index + 1,
    confidence: Math.round(item.confidence_score * 100),
    emotion: item.emotion
  }));

  return (
    <div className="p-5 sm:p-8">
      <h2 className="text-3xl font-extrabold text-slate-950">Mood History</h2>
      <p className="mt-2 text-slate-500">A lightweight dashboard of your saved mood predictions over time.</p>
      {history.length === 0 ? (
        <div className="mt-10 rounded-3xl bg-white/75 p-8 text-center shadow-sm">
          <h3 className="text-xl font-bold text-slate-900">No mood data yet</h3>
          <p className="mt-2 text-slate-500">Send a chat message and your detected emotion will appear here.</p>
        </div>
      ) : (
        <div className="mt-8 grid gap-5 xl:grid-cols-2">
          <section className="rounded-3xl bg-white/75 p-5 shadow-sm">
            <h3 className="mb-4 font-bold">Mood frequency</h3>
            <div className="h-72">
              <ResponsiveContainer>
                <BarChart data={frequency}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="emotion" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#14b8a6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>
          <section className="rounded-3xl bg-white/75 p-5 shadow-sm">
            <h3 className="mb-4 font-bold">Recent confidence trend</h3>
            <div className="h-72">
              <ResponsiveContainer>
                <LineChart data={trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="index" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip formatter={(value, name, item) => [`${value}%`, item.payload.emotion]} />
                  <Line type="monotone" dataKey="confidence" stroke="#ec4899" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
