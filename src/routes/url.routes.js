const express = require('express');
const urlController = require('../controllers/url.controller');

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


// Generate QR code
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