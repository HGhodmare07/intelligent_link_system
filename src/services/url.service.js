const base62 = require('./base62.service');
const urlModel = require('../models/url.model');
const cacheService = require('./cache.service');
const routingService = require('./routing.service');
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

  // Detect device
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

  // Check Redis
  const cachedUrl = await cacheService.getUrl(shortCode);
   
  console.log('Detected device:', device);
  
  let row;

  if (cachedUrl) {
    console.log(`Redis HIT: ${shortCode}`);

    row = await urlModel.findByShortCode(shortCode);

    if (!row) {
      return null;
    }

    await urlModel.incrementClicks(row.id);

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

    // Intelligent routing
    const routedUrl = await routingService.resolveRoute(
      row.id,
      device
    );

    return {
      ...row,
      original_url: routedUrl || cachedUrl
    };
  }

  console.log(`Redis MISS: ${shortCode}`);

  row = await urlModel.findByShortCode(shortCode);

  if (!row) {
    return null;
  }

  // Store original URL in Redis
  await cacheService.setUrl(
    shortCode,
    row.original_url
  );

  await urlModel.incrementClicks(row.id);

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

  // Intelligent routing
  const routedUrl = await routingService.resolveRoute(
    row.id,
    device
  );

  return {
    ...row,
    original_url: routedUrl || row.original_url
  };
}

async function getShortUrl(shortCode) {
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

  console.log(`Redis MISS: ${shortCode}`);

  const row = await urlModel.findByShortCode(shortCode);

  if (!row) {
    return null;
  }

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