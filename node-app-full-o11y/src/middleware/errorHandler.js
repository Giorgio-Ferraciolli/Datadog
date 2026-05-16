'use strict';

// ============================================================================
// Global error handler.
// - Marks the active APM span as errored (error=true + error.* tags).
// - Emits an app.errors.count metric.
// - Returns a clean JSON error to the client.
// ============================================================================

const tracer = require('dd-trace');
const logger = require('../utils/logger');
const metrics = require('../utils/metrics');

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, _next) {
  const status = err.status || 500;

  // Attach error info to the currently active span, if any.
  const span = tracer.scope().active();
  if (span) {
    span.setTag('error', true);
    span.setTag('error.type', err.name || 'Error');
    span.setTag('error.message', err.message);
    span.setTag('error.stack', err.stack);
    span.setTag('http.status_code', status);
  }

  const endpoint = (req.route && req.route.path) || req.path || 'unknown';
  metrics.increment('errors.count', 1, [
    `endpoint:${endpoint}`,
    `method:${req.method}`,
    `error_type:${err.name || 'Error'}`,
  ]);

  logger.error(
    {
      err: { message: err.message, stack: err.stack, name: err.name },
      method: req.method,
      url: req.originalUrl,
      status,
    },
    'request failed',
  );

  res.status(status).json({
    error: err.name || 'Error',
    message: err.message,
  });
}

module.exports = errorHandler;
