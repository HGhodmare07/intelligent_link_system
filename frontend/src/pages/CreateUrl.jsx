import { useState } from "react";
import { Link } from "react-router-dom";
import UrlForm from "../components/UrlForm.jsx";
import SecurityCard from "../components/SecurityCard.jsx";
import CopyButton from "../components/CopyButton.jsx";

export default function CreateUrl() {
  const [result, setResult] = useState(null);
  const [blocked, setBlocked] = useState(null);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Create URL</h1>
          <p className="muted">Every URL is checked by the ML security service before a short link is created.</p>
        </div>
      </div>

      <UrlForm
        onCreated={(r) => { setBlocked(null); setResult(r); }}
        onBlocked={(b) => { if (b) setResult(null); setBlocked(b); }}
      />

      {blocked && (
        <>
          <div className="alert alert-danger" role="alert">
            <strong>URL blocked by security validation.</strong> No short URL was created.
          </div>
          <SecurityCard blocked security={blocked.security} />
        </>
      )}

      {result && (
        <>
          <SecurityCard security={result.security} />
          <div className="card">
            <h3>Short URL</h3>
            <div className="row">
              <a className="short-url" href={result.shortUrl} target="_blank" rel="noreferrer">{result.shortUrl}</a>
              <CopyButton text={result.shortUrl} />
            </div>
            <p className="muted">Points to {result.originalUrl}</p>
            <div className="row">
              <Link className="btn btn-ghost" to={`/urls/${result.shortCode}`}>View details and QR</Link>
              <Link className="btn btn-ghost" to={`/routing/${result.shortCode}`}>Manage routes</Link>
              <Link className="btn btn-ghost" to={`/analytics/${result.shortCode}`}>View analytics</Link>
            </div>
          </div>
        </>
      )}
    </>
  );
}
