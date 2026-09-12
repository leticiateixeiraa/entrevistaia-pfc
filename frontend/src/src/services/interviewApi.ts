// Service de integração com o backend FastAPI.
//
// Persiste a sessão no backend autenticado.

import type { InterviewRequest, InterviewResponse } from "@/types/interview";

const API_BASE_URL = import.meta.env["VITE_API_BASE_URL"] ?? "http://localhost:8000";
export class ApiError extends Error {
  readonly status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function createInterviewReal(
  request: InterviewRequest,
): Promise<InterviewResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/interviews`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("access_token") ?? ""}`,
      },
      body: JSON.stringify(request),
    });
  } catch {
    throw new ApiError("Não foi possível conectar ao servidor. Verifique sua conexão.");
  }

  if (!response.ok) {
    // O backend retorna erros no padrão { "detail": "mensagem" }.
    let detail: string | undefined;
    try {
      const body = (await response.json()) as { detail?: string };
      detail = body.detail;
    } catch {
      detail = undefined;
    }
    throw new ApiError(
      detail ?? "Não foi possível gerar as perguntas. Tente novamente.",
      response.status,
    );
  }

  const body = (await response.json()) as {
    session_id: string;
    questions: Array<string | { order: number; text: string }>;
  };

  return {
    session_id: body.session_id,
    questions: body.questions.map((question, index) =>
      typeof question === "string" ? { order: index + 1, text: question } : question,
    ),
  };
}

export async function createInterview(
  request: InterviewRequest,
): Promise<InterviewResponse> {
  return createInterviewReal(request);
}
