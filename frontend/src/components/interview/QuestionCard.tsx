type QuestionCardProps = {
  questionText: string;
};

export function QuestionCard({ questionText }: QuestionCardProps) {
  return (
    <div className="w-full rounded-2xl border border-border bg-card px-6 py-12 text-center shadow-sm sm:px-12">
      <p className="text-xl font-semibold leading-relaxed text-card-foreground sm:text-2xl">
        “{questionText}”
      </p>
    </div>
  );
}
