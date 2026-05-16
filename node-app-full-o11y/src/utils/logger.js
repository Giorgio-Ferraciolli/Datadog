'use strict';

// ============================================================================
// Structured logger (pino) emitting JSON to stdout.
//
// dd-trace's `logInjection: true` automatically enriches each log record with
// trace_id, span_id, dd.service, dd.env, dd.version when there is an active
// span. We also add a `mixin` so those fields are present even without a span,
// which keeps the schema consistent.
// ============================================================================

const pino = require('pino');
const config = require('../config');

const logger = pino({
  level: config.app.logLevel,
  base: {
    'dd.service': config.datadog.service,
    'dd.env': config.datadog.env,
    'dd.version': config.datadog.version,
  },
  formatters: {
    // Emit the level as a string ("info") rather than the numeric pino default,
    // which is what the Datadog log pipeline expects.
    level(label) {
      return { level: label };
    },
  },
  // ISO timestamp under the "timestamp" key for Datadog's default parser.
  timestamp: () => `,"timestamp":"${new Date().toISOString()}"`,
  messageKey: 'message',
});

module.exports = logger;
