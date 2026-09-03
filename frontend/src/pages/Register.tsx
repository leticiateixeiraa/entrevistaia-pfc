// feat(auth-frontend): cria tela de cadastro com validação de formulário
import { useState, FormEvent } from "react";
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
      // TODO: redirecionar para a tela de login (ou já logar automaticamente)
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Não foi possível criar a conta.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Criar conta</h1>

      <label>
        Nome
        <input value={name} onChange={(e) => setName(e.target.value)} />
      </label>

      <label>
        E-mail
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </label>

      <label>
        Senha
        <input
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </label>

      {error && <p role="alert">{error}</p>}

      <button type="submit" disabled={loading}>
        {loading ? "Criando..." : "Criar conta"}
      </button>
    </form>
  );
}
