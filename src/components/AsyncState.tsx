import type { ReactNode } from "react";

export type RemoteState<T> =
  | { status: "loading" }
  | { status: "ready"; data: T }
  | { status: "error"; message: string };

export function LoadingState({ label }: { label: string }) {
  return (
    <div className="resource-state" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="resource-error" role="alert">
      <p>{message}</p>
      <button className="button secondary" onClick={onRetry}>
        Retry
      </button>
    </div>
  );
}

export function EmptyState({
  title,
  detail,
  children,
}: {
  title: string;
  detail: string;
  children?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <span className="empty-orbit" aria-hidden="true">⌕</span>
      <h3>{title}</h3>
      <p>{detail}</p>
      {children}
    </div>
  );
}
