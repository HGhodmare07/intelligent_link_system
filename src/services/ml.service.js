const ML_SERVICE_URL =
  process.env.ML_SERVICE_URL || 'http://127.0.0.1:8000';

async function checkUrl(url) {
  const response = await fetch(`${ML_SERVICE_URL}/check`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      url
    })
  });

  const data = await response.json();

  if (!response.ok) {
    const error = new Error(
      data.detail || 'ML URL validation failed.'
    );

    error.status = response.status;
    throw error;
  }

  return data;
}

module.exports = {
  checkUrl
};