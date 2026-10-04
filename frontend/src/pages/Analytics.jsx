import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import CodeLookup from "../components/CodeLookup.jsx";
import AnalyticsCard from "../components/AnalyticsCard.jsx";
import AnalyticsCharts from "../components/AnalyticsCharts.jsx";
import Loading, { ErrorMessage } from "../components/Loading.jsx";
import { getAnalytics, normalizeError } from "../services/api.js";

export default function Analytics() {
  const { code } = useParams();
  const navigate = useNavigate();
  const [state, setState] = useState({ loading: false });

  useEffect(() => {
    if (!code) return;
    let alive = true;
    setState({ loading: true });
    getAnalytics(code)
      .then((analytics) => alive && setState({ analytics }))
      .catch((err) => alive && setState({ error: normalizeError(err) }));
    return () => { alive = false; };
  }, [code]);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Analytics</h1>
          <p className="muted">Traffic for a single short code.</p>
        </div>
      </div>
      <CodeLookup initial={code || ""} buttonLabel="Load analytics" onSubmit={(c) => navigate(`/analytics/${encodeURIComponent(c)}`)} />
      {state.loading && <Loading label="Loading analytics..." />}
      <ErrorMessage error={state.error} />
      {state.analytics && (
        <>
          <div className="grid grid-2">
            <AnalyticsCard label="Total clicks" value={state.analytics.totalClicks} />
            <AnalyticsCard label="Unique visitors" value={state.analytics.uniqueVisitors ?? "N/A"} />
          </div>
          <AnalyticsCharts analytics={state.analytics} />
        </>
      )}
    </>
  );
}
