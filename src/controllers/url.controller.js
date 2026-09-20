const qrService = require('../services/qr.service');
const urlService = require('../services/url.service');
const analyticsService = require('../services/analytics.service');

function isValidUrl(value) {
  try {
    new URL(value);
    return true;
  } catch {
    return false;
  }
}

async function createShortUrl(req, res, next) {
  try {
    const { originalUrl } = req.body;

    if (!originalUrl || !isValidUrl(originalUrl)) {
      return res.status(400).json({
        error: 'A valid "originalUrl" is required.'
      });
    }

    const record = await urlService.shortenUrl(originalUrl);

    const baseUrl =
      process.env.BASE_URL || `${req.protocol}://${req.get('host')}`;

    return res.status(201).json({
      id: record.id,
      originalUrl: record.original_url,
      shortCode: record.short_code,
      shortUrl: `${baseUrl}/${record.short_code}`,
      createdAt: record.created_at
    });
  } catch (err) {
    next(err);
  }
}

async function redirectToOriginal(req, res, next) {
  try {
    const { code } = req.params;

    const record = await urlService.resolveShortCode(code, {
      ipAddress: req.ip,
      userAgent: req.get('user-agent'),
      referrer: req.get('referer')
    });

    if (!record) {
      return res.status(404).json({
        error: 'Short URL not found.'
      });
    }

    return res.redirect(302, record.original_url);
  } catch (err) {
    next(err);
  }
}

async function generateQr(req, res, next) {
  try {
    const { code } = req.params;

    const record = await urlService.getShortUrl(code);

    if (!record) {
      return res.status(404).json({
        error: 'Short URL not found.'
      });
    }

    const baseUrl =
      process.env.BASE_URL || `${req.protocol}://${req.get('host')}`;

    const shortUrl = `${baseUrl}/${record.short_code}`;

    const qrCode = await qrService.generateQrCode(shortUrl);

    return res.json({
      shortUrl,
      qrCode
    });
  } catch (err) {
    next(err);
  }
}
async function getAnalytics(req, res, next) {
  try {
    const { code } = req.params;

    const analytics =
      await analyticsService.getUrlAnalytics(code);

    if (!analytics) {
      return res.status(404).json({
        error: 'Short URL not found.'
      });
    }

    return res.json(analytics);

  } catch (err) {
    next(err);
  }
}

module.exports = {
  createShortUrl,
  redirectToOriginal,
  generateQr,
   getAnalytics
   
};