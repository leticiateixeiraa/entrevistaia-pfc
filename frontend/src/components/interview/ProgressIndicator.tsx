type ProgressIndicatorProps = {
  current: number;
  total: number;
};

export function ProgressIndicator({ current, total }: ProgressIndicatorProps) {
  const percent = (current / total) * 100;

  return (
    <div className="flex w-full flex-col gap-2">
      <p className="text-xs font-medium text-muted-foreground">
        Pergunta {current} de {total}
      </p>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-all duration-300"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
