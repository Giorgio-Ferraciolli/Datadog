'use strict';

// ============================================================================
// GET /users
// Demonstrates:
//   - Manual span creation with tracer.startSpan()
//   - Business tags on the span (user_id, count)
//   - Context propagation between async functions via tracer.scope().activate()
//   - Gauge metric (queue depth) using DogStatsD
// ============================================================================

const express = require('express');
const tracer = require('dd-trace');

const logger = require('../utils/logger');
const metrics = require('../utils/metrics');

const router = express.Router();

// Fake "queue" we report as a gauge to demonstrate the metric type.
let pendingJobs = 0;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Inner function that runs under a child span propagated from the route.
async function fetchUsersFromDb() {
  const parent = tracer.scope().active();
  const span = tracer.startSpan('db.query.users', { childOf: parent });
  span.setTag('db.type', 'postgres');
  span.setTag('db.statement', 'SELECT id, name FROM users LIMIT 10');

  try {
    // Activate the child span so anything awaited inside inherits it.
    return await tracer.scope().activate(span, async () => {
      const latency = 50 + Math.floor(Math.random() * 150);
      await sleep(latency);
      span.setTag('db.rows_returned', 3);
      return [
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' },
        { id: 3, name: 'Carol' },
      ];
    });
  } catch (err) {
    span.setTag('error', true);
    span.setTag('error.message', err.message);
    throw err;
  } finally {
    span.finish();
  }
}

router.get('/users', async (req, res, next) => {
  // Grab the request-scoped span that dd-trace's express integration created.
  const span = tracer.scope().active();
  if (span) {
    span.setTag('business.operation', 'list_users');
    span.setTag('user_id', req.query.user_id || 'anonymous');
  }

  pendingJobs += 1;
  metrics.gauge('queue.pending_jobs', pendingJobs);

  try {
    const users = await fetchUsersFromDb();
    logger.info({ count: users.length }, 'users listed');
    res.json({ users });
  } catch (err) {
    next(err);
  } finally {
    pendingJobs -= 1;
    metrics.gauge('queue.pending_jobs', pendingJobs);
  }
});

module.exports = router;
