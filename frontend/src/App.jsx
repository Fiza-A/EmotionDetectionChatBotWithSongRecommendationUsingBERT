import { Navigate, Route, Routes } from "react-router-dom";
import Shell from "./components/Shell";
import ChatPage from "./pages/ChatPage";
import HistoryPage from "./pages/HistoryPage";
import LoginPage from "./pages/LoginPage";
import PreferencesPage from "./pages/PreferencesPage";
import RegisterPage from "./pages/RegisterPage";
import { useAuth } from "./hooks/useAuth";

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="grid min-h-screen place-items-center font-semibold text-slate-600">Loading your space...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/"
        element={
          <Protected>
            <Shell />
          </Protected>
        }
      >
        <Route index element={<ChatPage />} />
        <Route path="preferences" element={<PreferencesPage />} />
        <Route path="history" element={<HistoryPage />} />
      </Route>
    </Routes>
  );
}
