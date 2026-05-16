'use strict';

// ============================================================================
// Express application.
// Loaded by tracer.js AFTER dd-trace is initialized.
// ============================================================================

const express = require('express');

const config = require('./config');
const logger = require('./utils/logger');
const metrics = require('./utils/metrics');

const requestMetrics = require('./middleware/requestMetrics');
const errorHandler = require('./middleware/errorHandler');

const healthRoutes = require('./routes/health');
const usersRoutes = require('./routes/users');
const ordersRoutes = require('./routes/orders');

const app = express();

app.disable('x-powered-by');
app.use(express.json({ limit: '1mb' }));
app.use(requestMetrics);

// Routes
app.use(healthRoutes);
app.use(usersRoutes);
app.use(ordersRoutes);

// 404 handler — funneled into the same error pipeline.
app.use((req, res, next) => {
  const err = new Error(`Not Found: ${req.method} ${req.originalUrl}`);
  err.name = 'NotFoundError';
  err.status = 404;
  next(err);
});

// Global error middleware (must be last).
app.use(errorHandler);

// ---------------------------------------------------------------------------
// Server start
// ---------------------------------------------------------------------------
const server = app.listen(config.app.port, '0.0.0.0', () => {
  logger.info(
    {
      port: config.app.port,
      env: config.datadog.env,
      service: config.datadog.service,
      version: config.datadog.version,
      agent_host: config.datadog.agentHost,
    },
    'server listening',
  );
});

// ---------------------------------------------------------------------------
// Process-level safety nets.
// We log, emit a metric, and shut down cleanly. Datadog will still receive
// the error because dd-trace flushes on exit hooks.
// ---------------------------------------------------------------------------
function shutdown(signal) {
  logger.info({ signal }, 'shutting down');
  server.close(() => {
    metrics.close(() => process.exit(0));
  });
  // Hard exit if we can't close in time.
  setTimeout(() => process.exit(1), 10_000).unref();
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

process.on('uncaughtException', (err) => {
  logger.fatal(
    { err: { message: err.message, stack: err.stack, name: err.name } },
    'uncaughtException',
  );
  metrics.increment('process.uncaught_exception', 1, [`error_type:${err.name || 'Error'}`]);
  // The Node docs recommend exiting after an uncaughtException; let the
  // orchestrator restart us.
  shutdown('uncaughtException');
});

process.on('unhandledRejection', (reason) => {
  const err = reason instanceof Error ? reason : new Error(String(reason));
  logger.error(
    { err: { message: err.message, stack: err.stack, name: err.name } },
    'unhandledRejection',
  );
  metrics.increment('process.unhandled_rejection', 1, [`error_type:${err.name || 'Error'}`]);
});

module.exports = app;
