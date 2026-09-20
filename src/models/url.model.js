const pool = require('../config/db');

async function insertUrl(originalUrl) {
  const result = await pool.query(
    `INSERT INTO urls (original_url)
     VALUES ($1)
     RETURNING id, original_url, created_at`,
    [originalUrl]
  );

  return result.rows[0];
}

async function setShortCode(id, shortCode) {
  const result = await pool.query(
    `UPDATE urls
     SET short_code = $1
     WHERE id = $2
     RETURNING *`,
    [shortCode, id]
  );

  return result.rows[0];
}

async function findByShortCode(shortCode) {
  const result = await pool.query(
    `SELECT *
     FROM urls
     WHERE short_code = $1`,
    [shortCode]
  );

  return result.rows[0] || null;
}

async function incrementClicks(id) {
  await pool.query(
    `UPDATE urls
     SET clicks = clicks + 1
     WHERE id = $1`,
    [id]
  );
}

async function insertClickEvent(
  urlId,
  ipAddress,
  userAgent,
  referrer,
  browser,
  browserVersion,
  os,
  osVersion,
  device
) {
  await pool.query(
    `INSERT INTO click_events
     (
       url_id,
       ip_address,
       user_agent,
       referrer,
       browser,
       browser_version,
       os,
       os_version,
       device
     )
     VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
    [
      urlId,
      ipAddress,
      userAgent,
      referrer,
      browser,
      browserVersion,
      os,
      osVersion,
      device
    ]
  );
}


// ==============================
// BASIC ANALYTICS
// ==============================

async function getAnalytics(urlId) {
  const result = await pool.query(
    `SELECT
       COUNT(*) AS total_clicks,
       COUNT(DISTINCT ip_address) AS unique_visitors
     FROM click_events
     WHERE url_id = $1`,
    [urlId]
  );

  return result.rows[0];
}


// ==============================
// BROWSER STATISTICS
// ==============================

async function getBrowserStats(urlId) {
  const result = await pool.query(
    `SELECT
       browser,
       COUNT(*) AS clicks
     FROM click_events
     WHERE url_id = $1
     GROUP BY browser
     ORDER BY clicks DESC`,
    [urlId]
  );

  return result.rows;
}


// ==============================
// OPERATING SYSTEM STATISTICS
// ==============================

async function getOsStats(urlId) {
  const result = await pool.query(
    `SELECT
       os,
       COUNT(*) AS clicks
     FROM click_events
     WHERE url_id = $1
     GROUP BY os
     ORDER BY clicks DESC`,
    [urlId]
  );

  return result.rows;
}


// ==============================
// DEVICE STATISTICS
// ==============================

async function getDeviceStats(urlId) {
  const result = await pool.query(
    `SELECT
       device,
       COUNT(*) AS clicks
     FROM click_events
     WHERE url_id = $1
     GROUP BY device
     ORDER BY clicks DESC`,
    [urlId]
  );

  return result.rows;
}


// ==============================
// REFERRER STATISTICS
// ==============================

async function getReferrerStats(urlId) {
  const result = await pool.query(
    `SELECT
       COALESCE(referrer, 'Direct') AS referrer,
       COUNT(*) AS clicks
     FROM click_events
     WHERE url_id = $1
     GROUP BY referrer
     ORDER BY clicks DESC`,
    [urlId]
  );

  return result.rows;
}


// ==============================
// RECENT CLICK EVENTS
// ==============================

async function getRecentClicks(urlId) {
  const result = await pool.query(
    `SELECT
       clicked_at,
       ip_address,
       browser,
       browser_version,
       os,
       os_version,
       device,
       referrer
     FROM click_events
     WHERE url_id = $1
     ORDER BY clicked_at DESC
     LIMIT 20`,
    [urlId]
  );

  return result.rows;
}


// ==============================
// DAILY CLICKS
// ==============================
// clicked_at is currently stored as
// TIMESTAMP WITHOUT TIME ZONE.
// PostgreSQL server timezone is already IST.
// Therefore, do NOT apply another timezone conversion.

async function getDailyClicks(urlId) {
  const result = await pool.query(
    `SELECT
       DATE(clicked_at) AS date,
       COUNT(*) AS clicks
     FROM click_events
     WHERE url_id = $1
     GROUP BY DATE(clicked_at)
     ORDER BY DATE(clicked_at) ASC`,
    [urlId]
  );

  return result.rows;
}


// ==============================
// HOURLY CLICKS
// ==============================
// clicked_at is already stored using
// the IST clock value.

async function getHourlyClicks(urlId) {
  const result = await pool.query(
    `SELECT
       DATE_TRUNC('hour', clicked_at) AS hour,
       COUNT(*) AS clicks
     FROM click_events
     WHERE url_id = $1
     GROUP BY DATE_TRUNC('hour', clicked_at)
     ORDER BY DATE_TRUNC('hour', clicked_at) ASC`,
    [urlId]
  );

  return result.rows;
}


// ==============================
// EXPORTS
// ==============================

module.exports = {
  insertUrl,
  setShortCode,
  findByShortCode,
  incrementClicks,
  insertClickEvent,
  getAnalytics,
  getBrowserStats,
  getOsStats,
  getDeviceStats,
  getReferrerStats,
  getRecentClicks,
  getDailyClicks,
  getHourlyClicks
};