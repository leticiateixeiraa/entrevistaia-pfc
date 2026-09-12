import { createFileRoute, Link, redirect, useNavigate } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { login, register } from "../../services/authService";

export const Route = createFileRoute("/register")({
  beforeLoad: () => {
    if (localStorage.getItem("access_token")) {
      throw redirect({ to: "/interview/setup" });
    }
  },
  component: RegisterPage,
});

function RegisterPage() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError("A senha precisa ter pelo menos 8 caracteres.");
      return;
    }

    setIsSubmitting(true);
    try {
      await register({ name, email, password });
      await login({ email, password });
      navigate({ to: "/interview/setup" });
    } catch (requestError: any) {
      setError(requestError?.response?.data?.detail ?? "Não foi possível criar a conta.");
      setIsSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4 py-12">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-2xl border border-border bg-card p-7 shadow-sm sm:p-9"
      >
        <p className="mb-2 text-sm font-semibold tracking-wide text-primary">EntrevistaIA</p>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Crie sua conta</h1>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          Comece a praticar sua comunicação com entrevistas simuladas.
        </p>

        <div className="mt-8 flex flex-col gap-5">
          <label className="flex flex-col gap-1.5 text-sm font-medium text-card-foreground">
            Nome
            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="rounded-lg border border-input bg-background px-3 py-2.5 font-normal text-foreground outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
            />
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium text-card-foreground">
            E-mail
            <input
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="rounded-lg border border-input bg-background px-3 py-2.5 font-normal text-foreground outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
            />
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium text-card-foreground">
            Senha
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="rounded-lg border border-input bg-background px-3 py-2.5 font-normal text-foreground outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
            />
          </label>
        </div>

        {error && <p className="mt-5 text-sm text-destructive" role="alert">{error}</p>}

        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-7 w-full rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Criando..." : "Criar conta"}
        </button>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          Já tem conta?{" "}
          <Link to="/" className="font-medium text-primary hover:underline">
            Entrar
          </Link>
        </p>
      </form>
    </main>
  );
}