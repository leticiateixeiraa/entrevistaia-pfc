import { useState, type FormEvent } from "react";
import { PRESENTATION_TYPES } from "@/types/interview";

export type InterviewFormValues = {
  jobTitle: string;
  presentationType: string;
  jobDescription: string;
};

type InterviewFormProps = {
  isSubmitting: boolean;
  onSubmit: (values: InterviewFormValues) => void;
};

export function InterviewForm({ isSubmitting, onSubmit }: InterviewFormProps) {
  const [jobTitle, setJobTitle] = useState("");
  const [presentationType, setPresentationType] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const isValid = jobTitle.trim().length > 0 && presentationType.length > 0;

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!isValid || isSubmitting) return;
    onSubmit({ jobTitle: jobTitle.trim(), presentationType, jobDescription: jobDescription.trim() });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex w-full flex-col gap-5 rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8"
    >
      <div className="flex flex-col gap-1.5">
        <label htmlFor="job-title" className="text-sm font-medium text-card-foreground">
          Vaga / Cargo
        </label>
        <input
          id="job-title"
          type="text"
          value={jobTitle}
          onChange={(e) => setJobTitle(e.target.value)}
          placeholder="Ex.: Analista de Dados"
          required
          className="rounded-lg border border-input bg-background px-3 py-2.5 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-primary focus:ring-2 focus:ring-primary/20"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="presentation-type" className="text-sm font-medium text-card-foreground">
          Tipo de entrevista
        </label>
        <select
          id="presentation-type"
          value={presentationType}
          onChange={(e) => setPresentationType(e.target.value)}
          required
          className="rounded-lg border border-input bg-background px-3 py-2.5 text-sm text-foreground outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/20"
        >
          <option value="" disabled>
            Selecione uma opção
          </option>
          {PRESENTATION_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1.5">
        <div className="flex items-baseline justify-between">
          <label htmlFor="job-description" className="text-sm font-medium text-card-foreground">
            Descrição da vaga{" "}
            <span className="font-normal text-muted-foreground">(opcional)</span>
          </label>
          {jobDescription.length > 0 && (
            <span className="text-xs text-muted-foreground">{jobDescription.length} caracteres</span>
          )}
        </div>
        <textarea
          id="job-description"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Cole aqui a descrição da vaga, requisitos ou principais responsabilidades."
          rows={5}
          className="resize-none rounded-lg border border-input bg-background px-3 py-2.5 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-primary focus:ring-2 focus:ring-primary/20"
        />
      </div>

      <button
        type="submit"
        disabled={!isValid || isSubmitting}
        className="mt-1 inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground transition-all hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting && (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground" />
        )}
        {isSubmitting ? "Preparando suas perguntas…" : "Gerar entrevista"}
      </button>
    </form>
  );
}
