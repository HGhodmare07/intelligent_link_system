import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import QrCodeCard from "../components/QrCodeCard.jsx";
import SecurityCard from "../components/SecurityCard.jsx";
import AnalyticsCard from "../components/AnalyticsCard.jsx";
import CopyButton from "../components/CopyButton.jsx";
import Loading, { ErrorMessage } from "../components/Loading.jsx";
import { API_BASE_URL, getAnalytics, getRoutes, listStoredUrls, normalizeError } from "../services/api.js";

export default function UrlDetails() {
  const { code } = useParams();
  const stored = listStoredUrls().find((u) => u.shortCode === code);
  const shortUrl = stored?.shortUrl || `${API_BASE_URL}/${code}`;
  const [stats, setStats] = useState({ loading: true });

  useEffect(() => {
    let alive = true;
    setStats({ loading: true });
    Promise.all([getAnalytics(code), getRoutes(code)])
      .then(([a, r]) => alive && setStats({ analytics: a, routes: r }))
      .catch((err) => alive && setStats({ error: normalizeError(err) }));
    return () => { alive = false; };
  }, [code]);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>URL details</h1>
          <p className="muted">Short code <code>{code}</code></p>
        </div>
      </div>

      <div className="card">
        <h3>Short URL</h3>
        <div className="row">
          <a className="short-url" href={shortUrl} target="_blank" rel="noreferrer">{shortUrl}</a>
          <CopyButton text={shortUrl} />
        </div>
        {stored?.originalUrl && <p className="muted">Original: {stored.originalUrl}</p>}
        <div className="row">
          <Link className="btn btn-ghost" to={`/routing/${code}`}>Manage routes</Link>
          <Link className="btn btn-ghost" to={`/analytics/${code}`}>Full analytics</Link>
        </div>
      </div>

      {stats.loading && <Loading label="Loading analytics..." />}
      <ErrorMessage error={stats.error} />
      {stats.analytics && (
        <div className="grid grid-3">
          <AnalyticsCard label="Total clicks" value={stats.analytics.totalClicks} />
          <AnalyticsCard label="Unique visitors" value={stats.analytics.uniqueVisitors ?? "N/A"} />
          <AnalyticsCard label="Routes" value={stats.routes.length} />
        </div>
      )}

      <QrCodeCard code={code} shortUrl={shortUrl} />
      {stored?.security && <SecurityCard security={stored.security} />}
    </>
  );
}
