const QRCode = require('qrcode');

async function generateQrCode(shortUrl) {
  return await QRCode.toDataURL(shortUrl);
}

module.exports = { generateQrCode };