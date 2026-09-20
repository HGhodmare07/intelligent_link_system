const UAParser = require('ua-parser-js');

function parseUserAgent(userAgent) {
  const parser = new UAParser(userAgent);

  const result = parser.getResult();

  return {
    browser: result.browser.name || 'Unknown',
    browserVersion: result.browser.version || 'Unknown',

    os: result.os.name || 'Unknown',
    osVersion: result.os.version || 'Unknown',

    device: result.device.type || 'Desktop'
  };
}

module.exports = {
  parseUserAgent
};