'use strict';

// ============================================================================
// DogStatsD client (hot-shots).
//
// The client ships metrics over UDP to the Datadog Agent. Global tags are
// attached to every metric so we can slice by service/env/version without
// repeating ourselves at every call site.
// ============================================================================

const StatsD = require('hot-shots');
const config = require('../config');
const logger = require('./logger');

const metrics = new StatsD({
  host: config.datadog.agentHost,
  port: config.datadog.dogstatsdPort,
  prefix: 'app.',
  globalTags: {
    service: config.datadog.service,
    env: config.datadog.env,
    version: config.datadog.version,
  },
  errorHandler: (error) => {
    // Never let metrics shipping crash the app.
    logger.warn({ err: error.message }, 'DogStatsD error');
  },
});

module.exports = metrics;
