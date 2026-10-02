const urlModel = require('../models/url.model');
const mlService = require('../services/ml.service');

function isValidUrl(value) {
  try {
    new URL(value);
    return true;
  } catch {
    return false;
  }
}

const ALLOWED_ROUTE_TYPES = [
  'default',
  'mobile',
  'tablet',
  'desktop'
];

async function addRoute(req, res, next) {
  try {
    const { code } = req.params;
    const { routeType, destinationUrl } = req.body;

    if (!routeType || !ALLOWED_ROUTE_TYPES.includes(routeType)) {
      return res.status(400).json({
        error: 'Invalid routeType.',
        allowed: ALLOWED_ROUTE_TYPES
      });
    }

    if (!destinationUrl || !isValidUrl(destinationUrl)) {
      return res.status(400).json({
        error: 'A valid destinationUrl is required.'
      });
    }
    const securityResult = await mlService.checkUrl(destinationUrl);

if (securityResult.decision === 'BLOCK') {
  return res.status(403).json({
    error: 'Route destination blocked by security validation.',
    security: securityResult
  });
}

    const url = await urlModel.findByShortCode(code);

    if (!url) {
      return res.status(404).json({
        error: 'Short URL not found.'
      });
    }

    const route = await urlModel.addRoute(
      url.id,
      routeType,
      destinationUrl
    );

    return res.status(201).json({
      message: 'Route created successfully.',
      route
    });
  } catch (err) {
    next(err);
  }
}

async function getRoutes(req, res, next) {
  try {
    const { code } = req.params;

    const url = await urlModel.findByShortCode(code);

    if (!url) {
      return res.status(404).json({
        error: 'Short URL not found.'
      });
    }

    const routes = await urlModel.getRoutes(url.id);

    return res.json({
      shortCode: code,
      urlId: url.id,
      routes
    });
  } catch (err) {
    next(err);
  }
}

module.exports = {
  addRoute,
  getRoutes
};