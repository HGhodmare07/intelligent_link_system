const pool = require('../config/db');

async function insertUrl(originalUrl) {
  const result = await pool.query(
    'INSERT INTO urls (original_url) VALUES ($1) RETURNING id, original_url, created_at',
    [originalUrl]
  );

  return result.rows[0];
}

async function setShortCode(id, shortCode) {
  const result = await pool.query(
    'UPDATE urls SET short_code = $1 WHERE id = $2 RETURNING *',
    [shortCode, id]
  );

  return result.rows[0];
}

async function findByShortCode(shortCode) {
  const result = await pool.query(
    'SELECT * FROM urls WHERE short_code = $1',
    [shortCode]
  );

  return result.rows[0] || null;
}

async function incrementClicks(id) {
  await pool.query(
    'UPDATE urls SET clicks = clicks + 1 WHERE id = $1',
    [id]
  );
}

module.exports = {
  insertUrl,
  setShortCode,
  findByShortCode,
  incrementClicks
};