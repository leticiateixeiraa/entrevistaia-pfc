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
  {
    value: "comportamental",
    label: "Comportamental",
    description: "Situações reais, decisões e resultados usando a estrutura STAR.",
  },
  {
    value: "tecnica",
    label: "Técnica",
    description: "Conhecimentos técnicos, raciocínio e resolução prática de problemas.",
  },
  {
    value: "mista",
    label: "Mista",
    description: "Entrevista equilibrada, combinando perguntas comportamentais e técnicas.",
  },
  {
    value: "apresentacao_pessoal",
    label: "Apresentação pessoal",
    description: "Trajetória, motivação, clareza e organização da sua narrativa.",
  },
] as const;

export function presentationTypeLabel(value: string): string {
  return PRESENTATION_TYPES.find((t) => t.value === value)?.label ?? value;
}
