import { useCallback, useEffect, useState } from "react";
import { createRoute, getRoutes, normalizeError } from "../services/api.js";
import Loading, { ErrorMessage } from "./Loading.jsx";
import SecurityCard from "./SecurityCard.jsx";

const TYPES = ["default", "mobile", "tablet", "desktop"];
const fmt = (t) => (t && !Number.isNaN(new Date(t).getTime()) ? new Date(t).toLocaleString() : "-");

export default function RouteManager({ code }) {
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState(null);
  const [routeType, setRouteType] = useState("mobile");
  const [destination, setDestination] = useState("");
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);
  const [blocked, setBlocked] = useState(null);
  const [success, setSuccess] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      setRoutes(await getRoutes(code));
    } catch (err) {
      setRoutes([]);
      setLoadError(normalizeError(err));
    } finally {
      setLoading(false);
    }
  }, [code]);

  useEffect(() => {
    setBlocked(null);
    setSuccess(false);
    load();
  }, [load]);

  async function submit(e) {
    e.preventDefault();
    setFormError(null);
    setBlocked(null);
    setSuccess(false);
    try {
      if (!["http:", "https:"].includes(new URL(destination.trim()).protocol)) throw new Error();
    } catch {
      setFormError({ kind: "validation", message: "Enter a full destination URL starting with http:// or https://" });
      return;
    }
    setSaving(true);
    try {
      await createRoute(code, routeType, destination.trim());
      setSuccess(true);
      setDestination("");
      await load();
    } catch (err) {
      const e2 = normalizeError(err);
      if (e2.kind === "blocked") setBlocked(e2);
      else setFormError(e2);
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <div className="card">
        <h3>Routes for <code>{code}</code></h3>
        {loading && <Loading label="Loading routes..." />}
        <ErrorMessage error={loadError} />
        {!loading && !loadError && routes.length === 0 && <p className="muted">No routes yet. Add one below.</p>}
        {routes.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Device type</th><th>Destination</th><th>Created</th></tr></thead>
              <tbody>
                {routes.map((r) => (
                  <tr key={r.id}>
                    <td><span className="badge">{r.routeType}</span></td>
                    <td className="cell-url">{r.destinationUrl}</td>
                    <td>{fmt(r.createdAt)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <form className="card form" onSubmit={submit}>
        <h3>Add route</h3>
        <label htmlFor="route-type">Route type</label>
        <select id="route-type" value={routeType} onChange={(e) => setRouteType(e.target.value)} disabled={saving}>
          {TYPES.map((t) => <option key={t} value={t}>{t[0].toUpperCase() + t.slice(1)}</option>)}
        </select>
        <label htmlFor="route-dest">Destination URL</label>
        <input id="route-dest" type="text" inputMode="url" placeholder="https://m.wikipedia.org" value={destination} onChange={(e) => setDestination(e.target.value)} disabled={saving} />
        <ErrorMessage error={formError} />
        {success && <div className="alert alert-ok" role="status">Route added. The destination passed the security check.</div>}
        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={saving || !destination.trim()}>
            {saving ? "Checking security..." : "Add route"}
          </button>
          {saving && <span className="muted">Creating route...</span>}
        </div>
      </form>

      {blocked && (
        <>
          <div className="alert alert-danger" role="alert"><strong>Route not created.</strong> The destination was blocked by security validation.</div>
          <SecurityCard blocked security={blocked.security} message="Destination blocked by security validation" />
        </>
      )}
    </>
  );
}
