// Armazena em memória a sessão de entrevista em andamento,
// para navegar da tela de configuração para a tela de perguntas.

import type { InterviewRequest, InterviewResponse } from "@/types/interview";

export type InterviewSession = {
  request: InterviewRequest;
  response: InterviewResponse;
};

let currentSession: InterviewSession | null = null;

export function saveInterviewSession(session: InterviewSession) {
  currentSession = session;
}

export function getInterviewSession(): InterviewSession | null {
  return currentSession;
}

export function clearInterviewSession() {
  currentSession = null;
}
