import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";

function App() {
  return (
    <div className="auth-shell">
      <div className="auth-panel">
        <div className="auth-brand">
          <h1>EntrevistaIA</h1>
          <p>Porque uma boa oportunidade começa com a confiança de saber se comunicar.</p>
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