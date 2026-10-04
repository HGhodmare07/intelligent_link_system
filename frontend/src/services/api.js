
import axios from "axios";

// The only place a backend URL is defined.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:3000";
export { API_BASE_URL };

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: { "Content-Type": "application/json" },
});

/* ------------------------------------------------------------------ *
 * Response mapping
 * ------------------------------------------------------------------ */
export const ANALYTICS_MAP = {
  totalClicks: [
    "totalClicks",
    "total_clicks",
    "clicks",
    "total",
  ],

  uniqueVisitors: [
    "uniqueVisitors",
    "unique_visitors",
    "uniqueClicks",
    "unique",
  ],

  browsers: [
    "browsers",
    "browserStats",
    "browser_stats",
    "browser",
  ],

  operatingSystems: [
    "operatingSystems",
    "operating_systems",
    "os",
    "osStats",
    "os_stats",
  ],

  devices: [
    "devices",
    "deviceStats",
    "device_stats",
    "device",
  ],

  referrers: [
    "referrers",
    "referrerStats",
    "referrer_stats",
    "referrer",
  ],

  dailyClicks: [
    "dailyClicks",
    "daily_clicks",
    "daily",
    "clicksByDay",
    "clicks_by_day",
  ],

  hourlyClicks: [
    "hourlyClicks",
    "hourly_clicks",
    "hourly",
    "clicksByHour",
    "clicks_by_hour",
  ],

  recentClicks: [
    "recentClicks",
    "recent_clicks",
    "recent",
    "recentVisits",
  ],
};


const LABEL_KEYS = [
  "label",
  "name",
  "browser",
  "os",
  "operating_system",
  "device",
  "device_type",
  "referrer",
  "referer",
  "source",
  "date",
  "day",
  "hour",
  "key",
];

const COUNT_KEYS = [
  "count",
  "clicks",
  "total",
  "value",
  "visits",
  "hits",
];

const TIME_KEYS = [
  "clicked_at",
  "clickedAt",
  "timestamp",
  "created_at",
  "createdAt",
  "time",
];


const has = (v) =>
  v !== undefined && v !== null;


const pick = (obj, keys) => {
  const k = keys.find((key) =>
    has(obj?.[key])
  );

  return k
    ? obj[k]
    : undefined;
};


const num = (v) => {
  if (
    v === null ||
    v === undefined ||
    v === "" ||
    typeof v === "object"
  ) {
    return null;
  }

  const n = Number(v);

  return Number.isFinite(n)
    ? n
    : null;
};


/* ------------------------------------------------------------------ *
 * Distribution normalizer
 *
 * Backend examples:
 *
 * browsers:
 * [{ browser: "Unknown", clicks: 1 }]
 *
 * operatingSystems:
 * [{ os: "Windows", clicks: 1 }]
 *
 * devices:
 * [{ device: "Desktop", clicks: 1 }]
 *
 * referrers:
 * [{ referrer: "Direct", clicks: 1 }]
 *
 * UI format:
 * [{ label: "Windows", count: 1 }]
 * ------------------------------------------------------------------ */
function toDistribution(value) {
  if (!value) {
    return [];
  }

  if (Array.isArray(value)) {
    return value.map((item) => {
      if (
        item &&
        typeof item === "object"
      ) {
        const label =
          item.label ??
          item.name ??
          item.browser ??
          item.os ??
          item.operating_system ??
          item.device ??
          item.device_type ??
          item.referrer ??
          item.referer ??
          item.source ??
          item.date ??
          item.day ??
          item.hour ??
          item.key ??
          "";

        const count =
          item.count ??
          item.clicks ??
          item.total ??
          item.value ??
          item.visits ??
          item.hits ??
          0;

        return {
          label:
            String(label || "Direct"),

          count:
            num(count) ?? 0,
        };
      }

      return {
        label: String(item),
        count: 1,
      };
    });
  }

  if (typeof value === "object") {
    return Object.entries(value).map(
      ([label, count]) => ({
        label:
          label || "Direct",

        count:
          num(count) ?? 0,
      })
    );
  }

  return [];
}


export function normalizeAnalytics(raw) {
  const src = {
    ...(raw || {}),
    ...(raw?.summary || {}),
    ...(raw?.totals || {}),
    ...(raw?.data || {}),
    ...(raw?.analytics || {}),
  };


  /* ---------------- Daily clicks ---------------- */

  const daily = toDistribution(
    pick(
      src,
      ANALYTICS_MAP.dailyClicks
    )
  )
    .map((d) => ({
      ...d,
      label: String(
        d.label ?? ""
      ).slice(0, 10),
    }))
    .sort((a, b) =>
      a.label.localeCompare(b.label)
    );


  /* ---------------- Hourly clicks ---------------- */

  const hourlyRaw = toDistribution(
    pick(
      src,
      ANALYTICS_MAP.hourlyClicks
    )
  );


  const hourOf = (label) => {
    const value = String(
      label ?? ""
    );

    if (/^\d{1,2}$/.test(value)) {
      return Number(value);
    }

    const d = new Date(value);

    return Number.isNaN(
      d.getTime()
    )
      ? -1
      : d.getHours();
  };


  const hourly = Array.from(
    { length: 24 },
    (_, h) => ({
      label: String(h),

      count:
        hourlyRaw
          .filter(
            (x) =>
              hourOf(x.label) === h
          )
          .reduce(
            (s, x) =>
              s + x.count,
            0
          ),
    })
  );


  /* ---------------- Recent clicks ---------------- */

  const recentRaw = pick(
    src,
    ANALYTICS_MAP.recentClicks
  );


  const recent = (
    Array.isArray(recentRaw)
      ? recentRaw
      : []
  ).map((c) => ({
    time: pick(
      c,
      TIME_KEYS
    ),

    browser:
      pick(c, [
        "browser",
      ]) ?? "-",

    os:
      pick(c, [
        "os",
        "operating_system",
      ]) ?? "-",

    device:
      pick(c, [
        "device",
        "device_type",
      ]) ?? "-",

    referrer:
      pick(c, [
        "referrer",
        "referer",
      ]) || "Direct",
  }));


  /* ---------------- Total clicks ---------------- */

  const totalKey =
    ANALYTICS_MAP.totalClicks.find(
      (k) =>
        num(src[k]) !== null
    );


  /* ---------------- Unique visitors ---------------- */

  const uniqueKey =
    ANALYTICS_MAP.uniqueVisitors.find(
      (k) =>
        num(src[k]) !== null
    );


  /* ---------------- Final result ---------------- */

  return {
    totalClicks:
      totalKey
        ? num(src[totalKey])
        : daily.reduce(
            (s, d) =>
              s + d.count,
            0
          ),

    uniqueVisitors:
      uniqueKey
        ? num(src[uniqueKey])
        : null,

    browsers:
      toDistribution(
        pick(
          src,
          ANALYTICS_MAP.browsers
        )
      ),

    operatingSystems:
      toDistribution(
        pick(
          src,
          ANALYTICS_MAP.operatingSystems
        )
      ),

    devices:
      toDistribution(
        pick(
          src,
          ANALYTICS_MAP.devices
        )
      ),

    referrers:
      toDistribution(
        pick(
          src,
          ANALYTICS_MAP.referrers
        )
      ),

    dailyClicks:
      daily,

    hourlyClicks:
      hourly,

    recentClicks:
      recent,
  };
}


/* ------------------------------------------------------------------ *
 * Security normalization
 * ------------------------------------------------------------------ */

function normalizeSecurity(s) {
  if (
    !s ||
    typeof s !== "object"
  ) {
    return null;
  }

  const p =
    s.p_malicious ??
    s.pMalicious;

  if (
    !has(s.decision) &&
    !has(p) &&
    !has(s.most_likely_class)
  ) {
    return null;
  }

  return {
    decision:
      s.decision ?? "UNKNOWN",

    pMalicious:
      has(p)
        ? Number(p)
        : null,

    mostLikelyClass:
      s.most_likely_class ??
      s.mostLikelyClass ??
      "unknown",
  };
}


/* ------------------------------------------------------------------ *
 * QR normalization
 * ------------------------------------------------------------------ */

function extractQr(data) {
  if (
    typeof data === "string"
  ) {
    return data;
  }

  if (
    data &&
    typeof data === "object"
  ) {
    const hit =
      Object.values(data).find(
        (v) =>
          typeof v === "string" &&
          v.startsWith(
            "data:image"
          )
      );

    if (hit) {
      return hit;
    }
  }

  return null;
}


/* ------------------------------------------------------------------ *
 * Error handling
 * ------------------------------------------------------------------ */

export function normalizeError(err) {
  if (!err?.response) {
    if (
      err?.code ===
      "ECONNABORTED"
    ) {
      return {
        kind: "timeout",
        status: null,
        message:
          "The request took too long. The backend or the security service may be busy. Try again.",
      };
    }

    return {
      kind: "network",
      status: null,
      message:
        `Cannot reach the Node.js backend at ${API_BASE_URL}. Make sure it is running and allows requests from this page (CORS).`,
    };
  }

  const {
    status,
    data,
  } = err.response;

  const serverMessage =
    data &&
    typeof data === "object"
      ? data.error ||
        data.message
      : null;

  const security =
    normalizeSecurity(
      data?.security
    ) ||
    normalizeSecurity(data);

  if (status === 403) {
    return {
      kind: "blocked",
      status,
      message:
        "URL blocked by security validation",
      security,
    };
  }

  if (status === 400) {
    return {
      kind: "validation",
      status,
      message:
        serverMessage ||
        "The request was not valid. Check the URL or values you entered.",
    };
  }

  if (status === 404) {
    return {
      kind: "notfound",
      status,
      message:
        serverMessage ||
        "Nothing was found for that short code.",
    };
  }

  if (
    status === 502 ||
    status === 503 ||
    status === 504
  ) {
    return {
      kind: "ml_unavailable",
      status,
      message:
        "The security service (FastAPI, port 8000) is unavailable. Start it and try again.",
    };
  }

  return {
    kind: "server",
    status,
    message:
      "The server hit an error. If it keeps happening, check that the FastAPI security service is running.",
  };
}


/* ------------------------------------------------------------------ *
 * API calls
 * ------------------------------------------------------------------ */

const enc =
  encodeURIComponent;


export async function createShortUrl(
  originalUrl
) {
  const { data } =
    await client.post(
      "/api/urls",
      {
        originalUrl,
      }
    );

  return {
    ...data,
    security:
      normalizeSecurity(
        data.security
      ),
  };
}


export async function getRoutes(
  code
) {
  const { data } =
    await client.get(
      `/api/urls/${enc(code)}/routes`
    );

  return (
    data.routes || []
  ).map((r) => ({
    id: r.id,

    routeType:
      r.route_type ??
      r.routeType,

    destinationUrl:
      r.destination_url ??
      r.destinationUrl,

    createdAt:
      r.created_at ??
      r.createdAt,
  }));
}


export async function createRoute(
  code,
  routeType,
  destinationUrl
) {
  const { data } =
    await client.post(
      `/api/urls/${enc(code)}/routes`,
      {
        routeType,
        destinationUrl,
      }
    );

  return data;
}


export async function getAnalytics(
  code
) {
  const { data } =
    await client.get(
      `/api/urls/${enc(code)}/analytics`
    );

  return normalizeAnalytics(
    data
  );
}


export async function getQrCode(
  code
) {
  const { data } =
    await client.get(
      `/api/urls/${enc(code)}/qr`
    );

  const qr =
    extractQr(data);

  if (!qr) {
    throw new Error(
      "QR response did not contain an image"
    );
  }

  return qr;
}


export async function getHealth() {
  const { data } =
    await client.get(
      "/health"
    );

  return data;
}


/* ------------------------------------------------------------------ *
 * Local history
 * ------------------------------------------------------------------ */

const STORE_KEY =
  "ilr.urls";


export function listStoredUrls() {
  try {
    return (
      JSON.parse(
        localStorage.getItem(
          STORE_KEY
        )
      ) || []
    );
  } catch {
    return [];
  }
}


export function saveStoredUrl(
  entry
) {
  const item = {
    shortCode:
      entry.shortCode,

    shortUrl:
      entry.shortUrl,

    originalUrl:
      entry.originalUrl,

    createdAt:
      entry.createdAt,

    security:
      entry.security,
  };

  const rest =
    listStoredUrls().filter(
      (u) =>
        u.shortCode !==
        item.shortCode
    );

  try {
    localStorage.setItem(
      STORE_KEY,
      JSON.stringify(
        [
          item,
          ...rest,
        ].slice(0, 50)
      )
    );
  } catch {
    /* storage unavailable: dashboard history is optional */
  }
}

