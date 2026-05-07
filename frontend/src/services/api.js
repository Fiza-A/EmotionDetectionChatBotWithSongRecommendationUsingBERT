import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000"
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("emotion_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  register: (payload) => api.post("/auth/register", payload),
  login: (payload) => api.post("/auth/login", payload),
  me: () => api.get("/users/me")
};

export const userApi = {
  updatePreferences: (preferred_languages) => api.put("/users/preferences", { preferred_languages })
};

export const chatApi = {
  send: (message, conversation_id) => api.post("/chat/message", { message_text: message, conversation_id }),
  history: () => api.get("/chat/history"),
  moodHistory: () => api.get("/mood/history")
};

export const conversationApi = {
  create: (title) => api.post("/conversations", title ? { title } : {}),
  list: () => api.get("/conversations"),
  detail: (conversationId) => api.get(`/conversations/${conversationId}`),
  rename: (conversationId, title) => api.patch(`/conversations/${conversationId}`, { title }),
  delete: (conversationId) => api.delete(`/conversations/${conversationId}`)
};

export const recommendationApi = {
  feedback: (payload) => api.post("/recommendations/feedback", payload),
  list: (emotion = "neutral") => api.get("/recommendations", { params: { emotion } })
};
