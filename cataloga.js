// api/cataloga.js

module.exports = (req, res) => {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*'); // Allow all origins, or specify a particular origin
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight OPTIONS request
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Extract query parameters
  const { pair, ofset, api } = req.query;

  if (!pair || !ofset || !api) {
    res.status(400).json({ error: 'Missing required query parameters' });
    return;
  }

  // Handle your actual API logic here
  const data = {
    pair,
    ofset: parseInt(ofset, 10),
    api: parseInt(api, ''),
  };

  res.status(200).json(data);
};
