import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../services/authService";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login({ email, password });
      navigate("/welcome");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "E-mail ou senha inválidos.");
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2 className="font-display text-2xl font-semibold mb-8">Entrar</h2>

      <div className="mb-5 text-left">
        <label htmlFor="login-email" className="block text-sm text-text-400 mb-1.5">
          E-mail
        </label>
        <input
          id="login-email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full bg-ink-800 border border-ink-700 rounded px-3 py-2.5 text-sm text-text-100 focus:outline-none focus:border-amber-500"
        />
      </div>

      <div className="mb-5 text-left">
        <label htmlFor="login-password" className="block text-sm text-text-400 mb-1.5">
          Senha
        </label>
        <input
          id="login-password"
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full bg-ink-800 border border-ink-700 rounded px-3 py-2.5 text-sm text-text-100 focus:outline-none focus:border-amber-500"
        />
      </div>

      {error && (
        <p role="alert" className="text-red-400 text-sm -mt-2 mb-5">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-amber-500 text-ink-950 rounded py-3 font-semibold text-sm cursor-pointer hover:bg-amber-400 disabled:opacity-60 disabled:cursor-default"
      >
        {loading ? "Entrando..." : "Entrar"}
      </button>

      <p className="mt-6 text-sm text-text-400">
        Ainda não tem conta?{" "}
        <Link to="/register" className="text-amber-500 hover:underline">
          Criar conta
        </Link>
      </p>
    </form>
  );
}