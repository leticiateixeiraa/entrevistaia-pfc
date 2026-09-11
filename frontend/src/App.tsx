import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-sm bg-ink-900 border border-ink-700 rounded-lg p-10">
        <div className="mb-8">
          <h1 className="font-display text-2xl font-semibold tracking-tight">
            EntrevistaIA
          </h1>
          <p className="font-display italic font-medium text-amber-400 mt-2.5 leading-snug">
            Porque uma boa oportunidade começa com a confiança de saber se comunicar.
          </p>
        </div>

        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;