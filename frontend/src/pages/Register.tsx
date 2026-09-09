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
    <form className="auth-form" onSubmit={handleSubmit}>
      <h2>Criar conta</h2>

      <div className="field">
        <label htmlFor="register-name">Nome</label>
        <input
          id="register-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="register-email">E-mail</label>
        <input
          id="register-email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="register-password">Senha</label>
        <input
          id="register-password"
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>

      {error && <p className="error-text" role="alert">{error}</p>}

      <button className="btn-primary" type="submit" disabled={loading}>
        {loading ? "Criando..." : "Criar conta"}
      </button>

      <p className="auth-switch">
        Já tem conta? <Link to="/login">Entrar</Link>
      </p>
    </form>
  );
}