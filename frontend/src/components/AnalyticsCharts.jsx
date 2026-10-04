import Plot from "react-plotly.js";

// Format labels safely
const formatLabel = (label) => {
  const value = String(label ?? "").trim();
  return value || "Unknown";
};

// Format timestamps
const fmt = (t) => {
  if (!t) return "-";

  const d = new Date(t);

  return !Number.isNaN(d.getTime())
    ? d.toLocaleString()
    : "-";
};

// Empty chart state
function EmptyChart({ title }) {
  return (
    <div className="card analytics-chart-card">
      <h3>{title}</h3>
      <p className="muted">No data yet.</p>
    </div>
  );
}

// Compact breakdown for browsers, OS, devices and referrers
function BarList({ title, data }) {
  const items = Array.isArray(data) ? data : [];

  const sorted = items
    .map((d) => ({
      label: formatLabel(d.label),
      count: Math.max(0, Number(d.count) || 0),
    }))
    .filter((d) => d.count > 0)
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  if (sorted.length === 0) {
    return <EmptyChart title={title} />;
  }

  const maxCount = Math.max(
    ...sorted.map((d) => d.count)
  );

  const total = sorted.reduce(
    (sum, d) => sum + d.count,
    0
  );

  return (
    <div className="card analytics-chart-card">
      <h3>{title}</h3>

      <div className="analytics-breakdown">
        {sorted.map((item, index) => (
          <div
            className="breakdown-item"
            key={`${item.label}-${index}`}
          >
            <div className="breakdown-heading">
              <span
                className="breakdown-label"
                title={item.label}
              >
                {item.label}
              </span>

              <span className="breakdown-count">
                {item.count}
              </span>
            </div>

            <div
              className="breakdown-track"
              role="progressbar"
              aria-label={`${item.label}: ${item.count} clicks`}
              aria-valuenow={item.count}
              aria-valuemin={0}
              aria-valuemax={maxCount}
            >
              <div
                className="breakdown-fill"
                style={{
                  width: `${(item.count / maxCount) * 100}%`,
                }}
              />
            </div>

            <div className="breakdown-percentage">
              {((item.count / total) * 100).toFixed(1)}% of clicks
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Plotly configuration for time-based charts
const plotConfig = {
  responsive: true,
  displayModeBar: false,
  displaylogo: false,
  scrollZoom: false,
};

// Daily and hourly click charts
function ClickChart({
  title,
  data,
  every = 1,
}) {
  const items = Array.isArray(data) ? data : [];

  const normalized = items.map((d) => ({
    label: formatLabel(d.label),
    count: Math.max(0, Number(d.count) || 0),
  }));

  if (
    normalized.length === 0 ||
    normalized.every((d) => d.count === 0)
  ) {
    return <EmptyChart title={title} />;
  }

  const labels = normalized.map((d) => d.label);
  const counts = normalized.map((d) => d.count);

  const maxCount = Math.max(...counts);
  const yMax = Math.max(1, Math.ceil(maxCount * 1.3));

  const tickStep =
    maxCount <= 10 ? 1 : Math.ceil(yMax / 5);

  const step = Math.max(1, Number(every) || 1);

  // Select only the labels that should appear
  const tickvals = labels.filter(
    (_, index) => index % step === 0
  );

  const ticktext = tickvals.map((label) =>
    label.replace(/^\d{4}-/, "")
  );

  return (
    <div className="card analytics-chart-card">
      <h3>{title}</h3>

      <div className="chart-container">
        <Plot
          data={[
            {
              type: "bar",
              x: labels,
              y: counts,
              text: counts.map((count) =>
                count > 0 ? String(count) : ""
              ),
              textposition: "outside",
              cliponaxis: false,
              marker: {
                color: "#0e7c7b",
                line: {
                  width: 0,
                },
              },
              hovertemplate:
                "%{x}<br>Clicks: %{y}<extra></extra>",
            },
          ]}
          layout={{
            autosize: true,
            height: 320,

            margin: {
              l: 50,
              r: 20,
              t: 30,
              b: 75,
            },

            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",

            bargap: 0.3,
            showlegend: false,

            font: {
              family:
                "Segoe UI, system-ui, Arial, sans-serif",
              size: 12,
              color: "#5d6c73",
            },

            xaxis: {
              type: "category",
              tickmode: "array",
              tickvals,
              ticktext,
              automargin: true,
              tickangle: 0,
              tickfont: {
                size: 10,
              },
              fixedrange: true,
              showgrid: false,
            },

            yaxis: {
              title: {
                text: "Clicks",
                font: {
                  size: 12,
                },
              },
              rangemode: "tozero",
              range: [0, yMax],
              dtick: tickStep,
              automargin: true,
              fixedrange: true,
              gridcolor: "rgba(128,128,128,0.15)",
              zeroline: true,
            },
          }}
          config={plotConfig}
          style={{
            width: "100%",
            height: "320px",
          }}
          useResizeHandler
        />
      </div>
    </div>
  );
}

// Main analytics component
export default function AnalyticsCharts({
  analytics,
}) {
  if (!analytics) {
    return null;
  }

  const dailyClicks = Array.isArray(
    analytics.dailyClicks
  )
    ? analytics.dailyClicks
    : [];

  const hourlyClicks = Array.isArray(
    analytics.hourlyClicks
  )
    ? analytics.hourlyClicks
    : [];

  const browsers = Array.isArray(
    analytics.browsers
  )
    ? analytics.browsers
    : [];

  const operatingSystems = Array.isArray(
    analytics.operatingSystems
  )
    ? analytics.operatingSystems
    : [];

  const devices = Array.isArray(
    analytics.devices
  )
    ? analytics.devices
    : [];

  const referrers = Array.isArray(
    analytics.referrers
  )
    ? analytics.referrers
    : [];

  const recentClicks = Array.isArray(
    analytics.recentClicks
  )
    ? analytics.recentClicks
    : [];

  const dailyEvery = Math.max(
    1,
    Math.ceil(dailyClicks.length / 8)
  );

  return (
    <>
      {/* Browser, OS, device and referrer breakdowns */}
      <div className="grid grid-2 analytics-grid">
        <BarList
          title="Browsers"
          data={browsers}
        />

        <BarList
          title="Operating systems"
          data={operatingSystems}
        />

        <BarList
          title="Devices"
          data={devices}
        />

        <BarList
          title="Referrers"
          data={referrers}
        />
      </div>

      {/* Time-based analytics */}
      <div className="grid grid-2 analytics-grid">
        <ClickChart
          title="Daily clicks"
          data={dailyClicks}
          every={dailyEvery}
        />

        <ClickChart
          title="Hourly clicks (0-23)"
          data={hourlyClicks}
          every={3}
        />
      </div>

      {/* Recent clicks table */}
      <div className="card analytics-table-card">
        <h3>Recent clicks</h3>

        {recentClicks.length === 0 ? (
          <p className="muted">
            No clicks recorded yet.
          </p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Browser</th>
                  <th>OS</th>
                  <th>Device</th>
                  <th>Referrer</th>
                </tr>
              </thead>

              <tbody>
                {recentClicks.map((c, i) => (
                  <tr key={c.id ?? c._id ?? i}>
                    <td>{fmt(c.time)}</td>
                    <td>{c.browser || "-"}</td>
                    <td>{c.os || "-"}</td>
                    <td>{c.device || "-"}</td>
                    <td className="cell-url">
                      {c.referrer || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}