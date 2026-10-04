import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import AnalyticsCard from "../components/AnalyticsCard.jsx";
import Loading from "../components/Loading.jsx";
import { getAnalytics, getHealth, listStoredUrls } from "../services/api.js";

const fmt = (t) => (t && !Number.isNaN(new Date(t).getTime()) ? new Date(t).toLocaleString() : "-");

export default function Dashboard() {
  const urls = listStoredUrls();
  const [health, setHealth] = useState({ state: "loading" });
  const [clicks, setClicks] = useState({ state: "loading", total: 0 });

  useEffect(() => {
    let alive = true;
    getHealth()
      .then((h) => alive && setHealth({ state: h?.status === "ok" ? "ok" : "down" }))
      .catch(() => alive && setHealth({ state: "down" }));

    if (urls.length === 0) {
      setClicks({ state: "done", total: 0 });
    } else {
      Promise.allSettled(urls.map((u) => getAnalytics(u.shortCode))).then((results) => {
        if (!alive) return;
        const ok = results.filter((r) => r.status === "fulfilled");
        setClicks({
          state: ok.length === 0 ? "error" : "done",
          total: ok.reduce((s, r) => s + (r.value.totalClicks || 0), 0),
        });
      });
    }
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const checked = urls.filter((u) => u.security).length;
  const allowed = urls.filter((u) => String(u.security?.decision).toUpperCase() === "ALLOW").length;

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Dashboard</h1>
          <p className="muted">Overview of URLs created from this browser. The backend has no list endpoint, so history is kept locally.</p>
        </div>
        <Link className="btn btn-primary" to="/create">Create URL</Link>
      </div>

      <div className="grid grid-4">
        <AnalyticsCard label="Total URLs" value={urls.length} />
        <AnalyticsCard label="Total clicks" value={clicks.state === "loading" ? "..." : clicks.state === "error" ? "N/A" : clicks.total} hint={clicks.state === "error" ? "Analytics unavailable" : undefined} />
        <AnalyticsCard label="Security checks" value={checked} hint={`${allowed} allowed`} />
        <AnalyticsCard
          label="System status"
          value={health.state === "loading" ? "Checking" : health.state === "ok" ? "Online" : "Offline"}
          tone={health.state === "ok" ? "ok" : health.state === "down" ? "danger" : undefined}
          hint="Node.js backend /health"
        />
      </div>

      <div className="card">
        <h3>Recent URLs</h3>
        {urls.length === 0 ? (
          <p className="muted">No URLs yet. <Link to="/create">Create your first short URL.</Link></p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Original URL</th><th>Short code</th><th>Security</th><th>Created</th></tr></thead>
              <tbody>
                {urls.slice(0, 10).map((u) => (
                  <tr key={u.shortCode}>
                    <td className="cell-url">{u.originalUrl}</td>
                    <td><Link to={`/urls/${u.shortCode}`}><code>{u.shortCode}</code></Link></td>
                    <td>{u.security ? <span className={`badge ${String(u.security.decision).toUpperCase() === "ALLOW" ? "badge-ok" : "badge-danger"}`}>{u.security.decision}</span> : "-"}</td>
                    <td>{fmt(u.createdAt)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {clicks.state === "loading" && urls.length > 0 && <Loading label="Loading analytics..." />}
    </>
  );
}
