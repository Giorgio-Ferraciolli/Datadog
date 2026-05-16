// ============================================================================
// ENTRY POINT — dd-trace MUST be initialized before ANY other require.
// This file is the only thing referenced by `npm start` / Dockerfile CMD.
// ============================================================================

'use strict';

const os = require('os');

// Initialize the Datadog tracer FIRST. No other application require above this.
const tracer = require('dd-trace').init({
  service: process.env.DD_SERVICE || 'datadog-node-app',
  env: process.env.DD_ENV || 'development',
  version: process.env.DD_VERSION || '1.0.0',
  hostname: process.env.DD_AGENT_HOST || 'datadog-agent',
  // Continuous profiler
  profiling: true,
  // Runtime metrics (event loop lag, GC, heap, etc.)
  runtimeMetrics: true,
  // Inject trace_id / span_id / dd.* into logs automatically
  logInjection: true,
  // Useful diagnostics in non-prod
  startupLogs: process.env.NODE_ENV !== 'production',
  // Tag every span with the container hostname for easier filtering
  tags: {
    'container.hostname': os.hostname(),
  },
});

// Expose tracer globally so other modules can grab the already-initialized
// instance without re-importing dd-trace (which would no-op anyway).
module.exports = tracer;

// Now that the tracer is live, boot the actual application.
require('./app');
