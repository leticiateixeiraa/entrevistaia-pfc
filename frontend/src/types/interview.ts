// Tipos compartilhados com o contrato do backend FastAPI.

export type InterviewRequest = {
  job_title: string;
  presentation_type: string;
  job_description?: string;
};

export type InterviewQuestion = {
  order: number;
  text: string;
};

export type InterviewResponse = {
  session_id: string;
  questions: InterviewQuestion[];
};

export const PRESENTATION_TYPES = [
  { value: "comportamental", label: "Comportamental" },
  { value: "tecnica", label: "Técnica" },
  { value: "mista", label: "Mista" },
  { value: "apresentacao_pessoal", label: "Apresentação pessoal" },
] as const;

export function presentationTypeLabel(value: string): string {
  return PRESENTATION_TYPES.find((t) => t.value === value)?.label ?? value;
}
