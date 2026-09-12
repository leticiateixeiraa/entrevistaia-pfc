export function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-10">
      <div className="h-10 w-10 animate-spin rounded-full border-2 border-primary/20 border-t-primary" />
      <p className="text-sm font-medium text-muted-foreground">
        A IA está preparando sua entrevista…
      </p>
    </div>
  );
}
