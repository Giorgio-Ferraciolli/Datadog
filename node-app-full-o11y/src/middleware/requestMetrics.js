'use strict';

// ============================================================================
// Per-request metrics middleware.
// Emits:
//   - app.requests.count    (counter, tags: endpoint, status_code, method)
//   - app.requests.latency  (histogram in ms, same tags)
// ============================================================================

const metrics = require('../utils/metrics');

function requestMetrics(req, res, next) {
  const startNs = process.hrtime.bigint();

  res.on('finish', () => {
    const durationMs = Number(process.hrtime.bigint() - startNs) / 1e6;

    // Prefer the matched route pattern over the raw URL to keep cardinality
    // under control (e.g. `/users/:id` instead of `/users/42`).
    const endpoint = (req.route && req.route.path) || req.path || 'unknown';

    const tags = [
      `endpoint:${endpoint}`,
      `method:${req.method}`,
      `status_code:${res.statusCode}`,
    ];

    metrics.increment('requests.count', 1, tags);
    metrics.histogram('requests.latency', durationMs, tags);
  });

  next();
}

module.exports = requestMetrics;
