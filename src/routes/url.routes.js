const express = require('express');
const urlController = require('../controllers/url.controller');
const {
  createLinkLimiter,
  redirectLimiter
} = require('../middlewares/rateLimiter');

const router = express.Router();

router.post(
  '/api/urls',
  createLinkLimiter,
  urlController.createShortUrl
);

router.get(
  '/api/urls/:code/qr',
  urlController.generateQr
);

router.get(
  '/:code',
  redirectLimiter,
  urlController.redirectToOriginal
);

module.exports = router;