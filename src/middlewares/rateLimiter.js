const rateLimit = require('express-rate-limit');

const createLinkLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 30,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    error: 'Too many links created from this IP. Please try again later.'
  }
});

const redirectLimiter = rateLimit({
  windowMs: 1 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    error: 'Too many requests. Please slow down.'
  }
});

module.exports = {
  createLinkLimiter,
  redirectLimiter
};