import { createFileRoute, Link, redirect, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { getCurrentUser, logout, type CurrentUser } from "../services/authService";
import {
  listInterviewHistory,
  type InterviewHistoryItem,
} from "../services/interviewHistoryApi";
import { presentationTypeLabel } from "../types/interview";

export const Route = createFileRoute("/home")({
  beforeLoad: () => {
    if (!localStorage.getItem("access_token")) {
      throw redirect({ to: "/" });
    }
  },
  head: () => ({
    meta: [
      { title: "Início — StartAI" },
      {
        name: "description",
        content: "Veja suas entrevistas anteriores e comece uma nova simulação.",
      },
    ],
  }),
  component: HomePage,
});

const categoryLabels: Record<string, string> = {
  entrevista_de_emprego: "Entrevista de emprego",
  apresentacao_academica: "Apresentação acadêmica",
};

function HomePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [interviews, setInterviews] = useState<InterviewHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadHome() {
      try {
        const [currentUser, history] = await Promise.all([
          getCurrentUser(),
          listInterviewHistory(),
        ]);
        setUser(currentUser);
        setInterviews(history);
      } catch {
        setError("Não foi possível carregar seu histórico.");
      } finally {
        setIsLoading(false);
      }
    }

    void loadHome();
  }, []);

  function handleLogout() {
    logout();
    navigate({ to: "/" });
  }

  const firstName = user?.name?.trim().split(" ")[0] || "estudante";

  return (
    <main className="min-h-screen bg-background px-4 py-8 sm:px-8 sm:py-10">
      <div className="mx-auto max-w-6xl">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-border pb-6">
          <div>
            <p className="text-sm font-semibold tracking-wide text-primary">StartAI</p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-foreground">
              Olá, {firstName}
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Continue praticando ou comece uma nova simulação.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <Link to="/audit" className="font-medium text-muted-foreground hover:text-foreground">
              Auditoria
            </Link>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-lg border border-border px-3 py-2 font-medium text-foreground hover:bg-accent"
            >
              Sair
            </button>
            <Link
              to="/interview/setup"
              className="rounded-lg bg-primary px-4 py-2.5 font-semibold text-primary-foreground hover:bg-primary/90"
            >
              Nova entrevista
            </Link>
          </div>
        </header>

        <section className="mt-10">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wider text-primary">Seu percurso</p>
              <h2 className="mt-2 text-2xl font-bold tracking-tight text-foreground">
                Entrevistas anteriores
              </h2>
            </div>
            {!isLoading && interviews.length > 0 && (
              <span className="text-sm text-muted-foreground">
                {interviews.length} {interviews.length === 1 ? "sessão" : "sessões"}
              </span>
            )}
          </div>

          {isLoading && (
            <div className="mt-6 rounded-xl border border-border bg-card p-8 text-sm text-muted-foreground">
              Carregando seu histórico...
            </div>
          )}

          {error && !isLoading && (
            <div className="mt-6 rounded-xl border border-destructive/30 bg-card p-8 text-sm text-destructive">
              {error}
            </div>
          )}

          {!isLoading && !error && interviews.length === 0 && (
            <div className="mt-6 rounded-xl border border-dashed border-border bg-card px-6 py-12 text-center">
              <h3 className="text-lg font-semibold text-foreground">Sua primeira prática começa aqui</h3>
              <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-muted-foreground">
                Faça uma entrevista simulada e acompanhe suas sessões nesta página.
              </p>
              <Link
                to="/interview/setup"
                className="mt-6 inline-flex rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90"
              >
                Começar agora
              </Link>
            </div>
          )}

          {!isLoading && !error && interviews.length > 0 && (
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {interviews.map((interview) => (
                <article
                  key={interview.session_id}
                  className="rounded-xl border border-border bg-card p-5 shadow-sm"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wider text-primary">
                        {categoryLabels[interview.category] ?? interview.category}
                      </p>
                      <h3 className="mt-2 text-lg font-semibold text-card-foreground">
                        {interview.presentation_type
                          ? presentationTypeLabel(interview.presentation_type)
                          : "Entrevista simulada"}
                      </h3>
                    </div>
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                        interview.finished
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-amber-100 text-amber-700"
                      }`}
                    >
                      {interview.finished ? "Concluída" : "Em andamento"}
                    </span>
                  </div>
                  <div className="mt-6 flex items-center justify-between border-t border-border pt-4 text-sm text-muted-foreground">
                    <span>{interview.answered_count} respostas registradas</span>
                    <time dateTime={interview.created_at}>
                      {new Date(interview.created_at).toLocaleDateString("pt-BR")}
                    </time>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
