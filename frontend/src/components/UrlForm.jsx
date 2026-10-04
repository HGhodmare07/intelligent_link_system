import { useState } from "react";
import { createShortUrl, normalizeError, saveStoredUrl } from "../services/api.js";

export default function UrlForm({ onCreated, onBlocked }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    try {
      const parsed = new URL(url.trim());
      if (!["http:", "https:"].includes(parsed.protocol)) throw new Error("protocol");
    } catch {
      setError({ kind: "validation", message: "Enter a full URL starting with http:// or https://" });
      return;
    }
    setLoading(true);
    onBlocked?.(null);
    try {
      const result = await createShortUrl(url.trim());
      saveStoredUrl(result);
      onCreated?.(result);
    } catch (err) {
      const e2 = normalizeError(err);
      if (e2.kind === "blocked") onBlocked?.(e2);
      else setError(e2);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card form" onSubmit={submit}>
      <label htmlFor="original-url">Original URL</label>
      <input id="original-url" type="text" inputMode="url" placeholder="https://www.wikipedia.org" value={url} onChange={(e) => setUrl(e.target.value)} disabled={loading} />
      {error && <div className="alert alert-warn" role="alert">{error.message}</div>}
      <div className="form-actions">
        <button className="btn btn-primary" type="submit" disabled={loading || !url.trim()}>
          {loading ? "Checking security..." : "Create short URL"}
        </button>
        {loading && <span className="muted">Creating URL...</span>}
      </div>
    </form>
  );
}
