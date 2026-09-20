const redisClient = require('../config/redis');

async function getUrl(shortCode) {
  return await redisClient.get(`url:${shortCode}`);
}

async function setUrl(shortCode, originalUrl) {
  await redisClient.set(`url:${shortCode}`, originalUrl, {
    EX: 3600
  });
}
async function deleteUrl(shortCode) {
  await redisClient.del(`url:${shortCode}`);
}

module.exports = {
  getUrl,
  setUrl,
  deleteUrl
};