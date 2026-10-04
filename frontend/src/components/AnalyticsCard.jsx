
import Plot from "react-plotly.js";

/* =========================================================
   STAT CARD
   ========================================================= */

function StatCard({ label, value, hint, tone }) {
  return (
    <div className={`card stat ${tone ? `stat-${tone}` : ""}`}>
      <div className="stat-label">{label ?? "-"}</div>
      <div className="stat-value">{value ?? 0}</div>
      {hint && <div className="stat-hint">{hint}</div>}
    </div>
  );
}

/* =========================================================
   DISTRIBUTION CHART
   ========================================================= */

function distributionChart(title, data, type = "pie") {
  const items = Array.isArray(data) ? data : [];

  if (!items.length) {
    return (
      <div className="card">
        <h3>{title}</h3>
        <p className="muted">No data available yet.</p>
      </div>
    );
  }

  const labels = items.map((item) =>
    String(item.label ?? "")
  );

  const values = items.map((item) =>
    Number(item.count) || 0
  );

  return (
    <div className="card">
      <h3>{title}</h3>

      <Plot
        data={[
          {
            labels,
            values,
            type,
            hole: type === "pie" ? 0.45 : 0,
            textinfo: "label+percent",
            hovertemplate:
              "%{label}<br>Clicks: %{value}<extra></extra>",
          },
        ]}
        layout={{
          autosize: true,
          height: 350,
          margin: {
            l: 40,
            r: 40,
            t: 20,
            b: 40,
          },
          showlegend: true,
        }}
        style={{
          width: "100%",
          height: "350px",
        }}
        useResizeHandler
        config={{
          responsive: true,
          displayModeBar: false,
        }}
      />
    </div>
  );
}

/* =========================================================
   DAILY + HOURLY CHART
   ========================================================= */

function timeChart(title, data, xTitle) {
  const items = Array.isArray(data) ? data : [];

  if (!items.length) {
    return (
      <div className="card">
        <h3>{title}</h3>
        <p className="muted">No data available yet.</p>
      </div>
    );
  }

  const isDaily = title === "Clicks Over Time";

  const xValues = items.map((item) =>
    String(item.label ?? "")
  );

  const yValues = items.map((item) => {
    const value = Number(item.count);
    return Number.isFinite(value) ? value : 0;
  });

  return (
    <div className="card">
      <h3>{title}</h3>

      <Plot
        data={[
          {
            x: xValues,
            y: yValues,

            /*
             * Daily:
             *   Vertical bar chart
             *
             * Hourly:
             *   Line + markers
             */
            type: isDaily ? "bar" : "scatter",
            mode: isDaily ? undefined : "lines+markers",

            connectgaps: false,

            hovertemplate:
              "%{x}<br>Clicks: %{y}<extra></extra>",

            /*
             * IMPORTANT:
             * Keep each date as an individual bar.
             */
            ...(isDaily
              ? {
                  width: 0.55,
                  offsetgroup: "daily",
                }
              : {}),
          },
        ]}
        layout={{
          autosize: true,
          height: 350,

          margin: {
            l: 55,
            r: 25,
            t: 20,
            b: 60,
          },

          xaxis: {
            title: xTitle,

            /*
             * Dates such as:
             *
             * 10-01
             * 10-02
             * 10-03
             *
             * are treated as separate categories.
             */
            type: "category",

            automargin: true,

            /*
             * Preserve the original order
             * returned by the backend.
             */
            categoryorder: "array",
            categoryarray: xValues,
          },

          yaxis: {
            title: "Clicks",
            rangemode: "tozero",
            autorange: true,
          },

          ...(isDaily
            ? {
                /*
                 * Space between daily bars.
                 */
                bargap: 0.35,
                bargroupgap: 0,
              }
            : {
                hovermode: "x unified",
              }),
        }}
        style={{
          width: "100%",
          height: "350px",
        }}
        useResizeHandler
        config={{
          responsive: true,
          displayModeBar: false,
        }}
      />
    </div>
  );
}

/* =========================================================
   TRAFFIC SOURCE BAR CHART
   ========================================================= */

function barChart(title, data) {
  const items = Array.isArray(data) ? data : [];

  if (!items.length) {
    return (
      <div className="card">
        <h3>{title}</h3>
        <p className="muted">No data available yet.</p>
      </div>
    );
  }

  const labels = items.map((item) =>
    String(item.label ?? "")
  );

  const values = items.map((item) =>
    Number(item.count) || 0
  );

  return (
    <div className="card">
      <h3>{title}</h3>

      <Plot
        data={[
          {
            x: labels,
            y: values,
            type: "bar",

            hovertemplate:
              "%{x}<br>Clicks: %{y}<extra></extra>",
          },
        ]}
        layout={{
          autosize: true,
          height: 350,

          margin: {
            l: 55,
            r: 25,
            t: 20,
            b: 70,
          },

          xaxis: {
            title: "Source",
            type: "category",
            automargin: true,
          },

          yaxis: {
            title: "Clicks",
            rangemode: "tozero",
          },

          bargap: 0.35,
        }}
        style={{
          width: "100%",
          height: "350px",
        }}
        useResizeHandler
        config={{
          responsive: true,
          displayModeBar: false,
        }}
      />
    </div>
  );
}

/* =========================================================
   MAIN ANALYTICS CARD
   ========================================================= */

export default function AnalyticsCard({
  label,
  value,
  hint,
  tone,

  /*
   * Analytics data is optional.
   * This allows the component to continue
   * working as a normal stat card.
   */
  analytics,
}) {
  return (
    <>
      {/* ===================================================
          STAT CARD
          =================================================== */}

      <StatCard
        label={label}
        value={value}
        hint={hint}
        tone={tone}
      />

      {/* ===================================================
          CHARTS
          Only render when analytics data exists.
          =================================================== */}

      {analytics && (
        <div className="analytics-charts">
          <div className="grid grid-2">

            {/* Daily clicks */}
            {timeChart(
              "Clicks Over Time",
              analytics.dailyClicks,
              "Date"
            )}

            {/* Hourly clicks */}
            {timeChart(
              "Clicks by Hour",
              analytics.hourlyClicks,
              "Hour"
            )}

            {/* Device distribution */}
            {distributionChart(
              "Device Distribution",
              analytics.devices
            )}

            {/* Browser distribution */}
            {distributionChart(
              "Browser Distribution",
              analytics.browsers
            )}

            {/* Operating system */}
            {distributionChart(
              "Operating System",
              analytics.operatingSystems
            )}

            {/* Traffic sources */}
            {barChart(
              "Traffic Sources",
              analytics.referrers
            )}

          </div>
        </div>
      )}
    </>
  );
}
