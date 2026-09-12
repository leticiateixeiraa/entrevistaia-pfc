import { createFileRoute, Link, redirect, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { ProgressIndicator } from "@/components/interview/ProgressIndicator";
import { QuestionCard } from "@/components/interview/QuestionCard";
import { getInterviewSession, clearInterviewSession } from "@/services/interviewSession";
import { presentationTypeLabel } from "@/types/interview";

export const Route = createFileRoute("/interview/questions")({
  beforeLoad: () => {
    if (!localStorage.getItem("access_token")) {
      throw redirect({ to: "/" });
    }
  },
  head: () => ({
    meta: [
      { title: "Entrevista simulada — EntrevistaIA" },
      {
        name: "description",
        content: "Navegue pelas perguntas geradas pela IA para a sua entrevista simulada.",
      },
      { property: "og:title", content: "Entrevista simulada — EntrevistaIA" },
      {
        property: "og:description",
        content: "Navegue pelas perguntas geradas pela IA para a sua entrevista simulada.",
      },
    ],
  }),
  component: InterviewQuestionsPage,
});

function InterviewQuestionsPage() {
  const navigate = useNavigate();
  const session = getInterviewSession();
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!session) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center bg-background px-4">
        <div className="max-w-md text-center">
          <h1 className="text-xl font-semibold text-foreground">Nenhuma entrevista em andamento</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Configure uma nova simulação para gerar suas perguntas.
          </p>
          <Link
            to="/interview/setup"
            className="mt-6 inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Configurar entrevista
          </Link>
        </div>
      </main>
    );
  }

  const { request, response } = session;
  const questions = [...response.questions].sort((a, b) => a.order - b.order);
  const currentQuestion = questions[currentIndex];
  if (!currentQuestion) return null;

  const isFirst = currentIndex === 0;
  const isLast = currentIndex === questions.length - 1;

  function handleFinish() {
    clearInterviewSession();
    navigate({ to: "/interview/setup" });
  }

  return (
    <main className="flex min-h-screen flex-col bg-background px-4 py-10">
      <div className="mx-auto flex w-full max-w-2xl flex-1 flex-col">
        <header className="mb-8 text-center">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Entrevista simulada</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {request.job_title} • {presentationTypeLabel(request.presentation_type)}
          </p>
        </header>

        <div className="mb-8">
          <ProgressIndicator current={currentIndex + 1} total={questions.length} />
        </div>

        <div className="flex flex-1 items-center justify-center">
          <QuestionCard questionText={currentQuestion.text} />
        </div>

        <nav className="mt-8 flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
            disabled={isFirst}
            className="rounded-lg border border-border bg-card px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-accent disabled:cursor-not-allowed disabled:opacity-50"
          >
            Pergunta anterior
          </button>

          {isLast ? (
            <button
              type="button"
              onClick={handleFinish}
              className="rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
            >
              Finalizar
            </button>
          ) : (
            <button
              type="button"
              onClick={() => setCurrentIndex((i) => Math.min(questions.length - 1, i + 1))}
              className="rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
            >
              Próxima pergunta
            </button>
          )}
        </nav>

        <div className="mt-6 text-center">
          <Link
            to="/interview/setup"
            className="text-sm text-muted-foreground underline-offset-4 transition-colors hover:text-foreground hover:underline"
          >
            Voltar para configuração
          </Link>
        </div>
      </div>
    </main>
  );
}
