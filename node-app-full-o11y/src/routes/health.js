'use strict';

const express = require('express');
const config = require('../config');

const router = express.Router();

// GET /health — liveness/readiness probe.
router.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    version: config.datadog.version,
    service: config.datadog.service,
    env: config.datadog.env,
    timestamp: new Date().toISOString(),
  });
});

module.exports = router;
