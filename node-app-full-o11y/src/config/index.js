'use strict';

// ============================================================================
// Centralized configuration. Every env var lookup in the codebase MUST go
// through this module so defaults and validation live in one place.
// ============================================================================

const config = {
  app: {
    port: parseInt(process.env.PORT, 10) || 3000,
    nodeEnv: process.env.NODE_ENV || 'development',
    logLevel: process.env.LOG_LEVEL || 'info',
  },

  datadog: {
    service: process.env.DD_SERVICE || 'datadog-node-app',
    env: process.env.DD_ENV || 'development',
    version: process.env.DD_VERSION || '1.0.0',
    agentHost: process.env.DD_AGENT_HOST || 'datadog-agent',
    // DogStatsD UDP port on the agent. 8125 is the default.
    dogstatsdPort: parseInt(process.env.DD_DOGSTATSD_PORT, 10) || 8125,
  },
};

module.exports = config;
