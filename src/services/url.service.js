const base62 = require('./base62.service');
const urlModel = require('../models/url.model');

async function shortenUrl(originalUrl) {
  const { id } = await urlModel.insertUrl(originalUrl);

  const shortCode = base62.encode(Number(id));

  const updated = await urlModel.setShortCode(id, shortCode);

  return updated;
}

async function resolveShortCode(shortCode) {
  const row = await urlModel.findByShortCode(shortCode);

  if (!row) return null;

  await urlModel.incrementClicks(row.id);

  return row;
}

module.exports = {
  shortenUrl,
  resolveShortCode
};