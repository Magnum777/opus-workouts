const https = require('https');
const querystring = require('querystring');
const apiKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im5vdmEuY29mb3VuZGVyQGdtYWlsLmNvbSIsImV4cCI6NDkyNjgwMzMxNSwianRpIjoiMjc2N2ViOTgtMTA0MC00OTM2LWJlOTAtNmE5MjFiMzU5Nzk2In0.ikiSzVi62W9uxU1q-35-lZ7PBH3YsaleSJ0ZRmEBsRg';
const tweet = 'Local Capsuleer Reports Complete Indifference To Operation Avalon Rewards, SKIN Design Elements JITA — In a development that has stunned EVE Online observers, one returning player has declared with absolute certainty that he, quote, could not give a rats about SKIN design elements or booster rewards. The announcement came as the player reviewed Operation Avalon loot drops on July 10. Source: https://evehermit.wordpress.com/2026/07/10/giving-a-rats/ #EVEOnline';
const postData = querystring.stringify({
  user: 'Eveonion',
  'platform[]': ['x', 'bluesky', 'discord'],
  title: tweet
});
const url = new URL('https://api.upload-post.com/api/upload_text');
const options = {
  hostname: url.hostname,
  path: url.pathname,
  method: 'POST',
  headers: {
    'Authorization': 'Apikey ' + apiKey,
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': Buffer.byteLength(postData)
  }
};
const req = https.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    console.log('Status:', res.statusCode);
    console.log('Response:', data);
  });
});
req.on('error', (e) => console.error('Error:', e.message));
req.write(postData);
req.end();