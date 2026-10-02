const express = require('express');
const urlController = require('../controllers/url.controller');
const routingController = require('../controllers/routing.controller');

const {
  createLinkLimiter,
  redirectLimiter
} = require('../middlewares/rateLimiter');

const router = express.Router();

// Create short URL
router.post(
  '/api/urls',
  createLinkLimiter,
  urlController.createShortUrl
);

// Intelligent routing
router.post(
  '/api/urls/:code/routes',
  routingController.addRoute
);

router.get(
  '/api/urls/:code/routes',
  routingController.getRoutes
);

// QR code
router.get(
  '/api/urls/:code/qr',
  urlController.generateQr
);

// Analytics
router.get(
  '/api/urls/:code/analytics',
  urlController.getAnalytics
);

// Redirect
router.get(
  '/:code',
  redirectLimiter,
  urlController.redirectToOriginal
);

module.exports = router;