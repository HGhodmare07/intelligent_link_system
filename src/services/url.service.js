const base62 = require('./base62.service');
const urlModel = require('../models/url.model');
const cacheService = require('./cache.service');
const UAParser = require('ua-parser-js');

async function shortenUrl(originalUrl) {

  const { id } = await urlModel.insertUrl(originalUrl);

  const shortCode = base62.encode(Number(id));

  const updated = await urlModel.setShortCode(id, shortCode);

  return updated;
}

async function resolveShortCode(shortCode, requestInfo = {}) {

  const {
    ipAddress = null,
    userAgent = null,
    referrer = null
  } = requestInfo;

  // Parse browser, OS and device information
  const parser = new UAParser(userAgent || '');
  const userAgentResult = parser.getResult();

  const browser =
    userAgentResult.browser.name || 'Unknown';

  const browserVersion =
    userAgentResult.browser.version || 'Unknown';

  const os =
    userAgentResult.os.name || 'Unknown';

  const osVersion =
    userAgentResult.os.version || 'Unknown';

  const device =
    userAgentResult.device.type || 'Desktop';

  // 1. Check Redis first
  const cachedUrl = await cacheService.getUrl(shortCode);

  if (cachedUrl) {

    console.log(`Redis HIT: ${shortCode}`);

    const row = await urlModel.findByShortCode(shortCode);

    if (!row) return null;

    // Increment click count
    await urlModel.incrementClicks(row.id);

    // Store click event with analytics data
    await urlModel.insertClickEvent(
      row.id,
      ipAddress,
      userAgent,
      referrer,
      browser,
      browserVersion,
      os,
      osVersion,
      device
    );

    return {
      ...row,
      original_url: cachedUrl
    };
  }

  // 2. Redis MISS → check PostgreSQL
  console.log(`Redis MISS: ${shortCode}`);

  const row = await urlModel.findByShortCode(shortCode);

  if (!row) return null;

  // 3. Store the URL in Redis
  await cacheService.setUrl(
    shortCode,
    row.original_url
  );

  // 4. Increment click count
  await urlModel.incrementClicks(row.id);

  // 5. Store click event with analytics data
  await urlModel.insertClickEvent(
    row.id,
    ipAddress,
    userAgent,
    referrer,
    browser,
    browserVersion,
    os,
    osVersion,
    device
  );

  return row;
}
async function getShortUrl(shortCode) {
  // 1. Check Redis first
  const cachedUrl = await cacheService.getUrl(shortCode);

  if (cachedUrl) {
    console.log(`Redis HIT: ${shortCode}`);

    const row = await urlModel.findByShortCode(shortCode);

    if (!row) {
      return null;
    }

    return {
      ...row,
      original_url: cachedUrl
    };
  }

  // 2. Redis MISS → PostgreSQL
  console.log(`Redis MISS: ${shortCode}`);

  const row = await urlModel.findByShortCode(shortCode);

  if (!row) {
    return null;
  }

  // 3. Cache the URL
  await cacheService.setUrl(
    shortCode,
    row.original_url
  );

  return row;
}

module.exports = {
  shortenUrl,
  resolveShortCode,
  getShortUrl
};