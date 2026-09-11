import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { register } from "../services/authService";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError("A senha precisa ter pelo menos 8 caracteres.");
      return;
    }

    setLoading(true);
    try {
      await register({ email, password, name });
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Não foi possível criar a conta.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2 className="font-display text-2xl font-semibold mb-8">Criar conta</h2>

      <div className="mb-5 text-left">
        <label htmlFor="register-name" className="block text-sm text-text-400 mb-1.5">
          Nome
        </label>
        <input
          id="register-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full bg-ink-800 border border-ink-700 rounded px-3 py-2.5 text-sm text-text-100 focus:outline-none focus:border-amber-500"
        />
      </div>

      <div className="mb-5 text-left">
        <label htmlFor="register-email" className="block text-sm text-text-400 mb-1.5">
          E-mail
        </label>
        <input
          id="register-email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full bg-ink-800 border border-ink-700 rounded px-3 py-2.5 text-sm text-text-100 focus:outline-none focus:border-amber-500"
        />
      </div>

      <div className="mb-5 text-left">
        <label htmlFor="register-password" className="block text-sm text-text-400 mb-1.5">
          Senha
        </label>
        <input
          id="register-password"
          type="password"
          required
          minLength={8}
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
        {loading ? "Criando..." : "Criar conta"}
      </button>

      <p className="mt-6 text-sm text-text-400">
        Já tem conta?{" "}
        <Link to="/login" className="text-amber-500 hover:underline">
          Entrar
        </Link>
      </p>
    </form>
  );
}