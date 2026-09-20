require('dotenv').config();

const app = require('./app');
const redisClient = require('./config/redis');

const PORT = process.env.PORT || 3000;

async function startServer() {
  try {
    await redisClient.connect();
    console.log('Redis connected successfully');

    app.listen(PORT, () => {
      console.log(`URL shortener listening on http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
  }
}

startServer();