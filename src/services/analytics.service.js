const urlModel = require('../models/url.model');

async function getUrlAnalytics(shortCode) {

  const url = await urlModel.findByShortCode(shortCode);

  if (!url) {
    return null;
  }

  const basic = await urlModel.getAnalytics(url.id);

  const browsers = await urlModel.getBrowserStats(url.id);

  const operatingSystems = await urlModel.getOsStats(url.id);

  const devices = await urlModel.getDeviceStats(url.id);

  const referrers = await urlModel.getReferrerStats(url.id);

  const recentClicks = await urlModel.getRecentClicks(url.id);

  const dailyClicks = await urlModel.getDailyClicks(url.id);

  const hourlyClicks = await urlModel.getHourlyClicks(url.id);

  return {
    url: {
      id: url.id,
      shortCode: url.short_code,
      originalUrl: url.original_url,
      createdAt: url.created_at
    },

    totalClicks: Number(basic.total_clicks),

    uniqueVisitors: Number(basic.unique_visitors),

    browsers: browsers.map(item => ({
      browser: item.browser,
      clicks: Number(item.clicks)
    })),

    operatingSystems: operatingSystems.map(item => ({
      os: item.os,
      clicks: Number(item.clicks)
    })),

    devices: devices.map(item => ({
      device: item.device,
      clicks: Number(item.clicks)
    })),

    referrers: referrers.map(item => ({
      referrer: item.referrer,
      clicks: Number(item.clicks)
    })),

    dailyClicks: dailyClicks.map(item => ({
      date: item.date,
      clicks: Number(item.clicks)
    })),

    hourlyClicks: hourlyClicks.map(item => ({
      hour: item.hour,
      clicks: Number(item.clicks)
    })),

    recentClicks
  };
}

module.exports = {
  getUrlAnalytics
};