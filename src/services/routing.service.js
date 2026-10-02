const urlModel = require('../models/url.model');

/**
 * Select destination based on device type.
 *
 * Priority:
 * 1. Device-specific route
 * 2. Default route
 * 3. Original URL
 */
async function resolveRoute(urlId, device) {
  const normalizedDevice =
    (device || 'desktop').toLowerCase();

  let routeType = 'desktop';

  if (normalizedDevice === 'mobile') {
    routeType = 'mobile';
  } else if (normalizedDevice === 'tablet') {
    routeType = 'tablet';
  }

  // 1. Check device-specific route
  const deviceRoute = await urlModel.getRoute(
    urlId,
    routeType
  );

  if (deviceRoute) {
    return deviceRoute.destination_url;
  }

  // 2. Check default route
  const defaultRoute = await urlModel.getRoute(
    urlId,
    'default'
  );

  if (defaultRoute) {
    return defaultRoute.destination_url;
  }

  // 3. Fallback to original URL
  const url = await urlModel.findById(urlId);

  return url ? url.original_url : null;
}

module.exports = {
  resolveRoute
};