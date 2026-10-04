export default function Loading({ label = "Loading..." }) {
  return (
    <div className="loading" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

export function ErrorMessage({ error }) {
  if (!error) return null;
  return (
    <div className={`alert ${error.kind === "blocked" ? "alert-danger" : "alert-warn"}`} role="alert">
      <strong>{error.message}</strong>
    </div>
  );
}
