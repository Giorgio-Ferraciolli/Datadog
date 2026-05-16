'use strict';

// ============================================================================
// POST /orders
// Demonstrates:
//   - Business-level tags on the span (order_id, user_id, product)
//   - Error path that flips through the global error handler when ?fail=true
//   - Custom counter for successful orders
// ============================================================================

const express = require('express');
const crypto = require('crypto');
const tracer = require('dd-trace');

const logger = require('../utils/logger');
const metrics = require('../utils/metrics');

const router = express.Router();

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function processPayment(orderId, amount) {
  const parent = tracer.scope().active();
  const span = tracer.startSpan('payment.process', { childOf: parent });
  span.setTag('order_id', orderId);
  span.setTag('payment.amount', amount);
  span.setTag('payment.provider', 'mock-gateway');

  try {
    return await tracer.scope().activate(span, async () => {
      await sleep(30 + Math.floor(Math.random() * 70));
      return { authorized: true, tx_id: crypto.randomUUID() };
    });
  } finally {
    span.finish();
  }
}

router.post('/orders', async (req, res, next) => {
  const orderId = crypto.randomUUID();
  const body = req.body || {};
  const userId = body.user_id || 'anonymous';
  const product = body.product || 'widget-001';
  const amount = Number(body.amount) || 99.9;

  // Enrich the request-scoped span with business context.
  const span = tracer.scope().active();
  if (span) {
    span.setTag('business.operation', 'create_order');
    span.setTag('order_id', orderId);
    span.setTag('user_id', userId);
    span.setTag('product', product);
  }

  try {
    // Simulable failure path.
    if (req.query.fail === 'true') {
      const err = new Error(`simulated failure while creating order ${orderId}`);
      err.name = 'OrderProcessingError';
      err.status = 500;
      throw err;
    }

    const payment = await processPayment(orderId, amount);

    metrics.increment('orders.created', 1, [
      `product:${product}`,
      `user_id:${userId}`,
    ]);

    logger.info(
      { order_id: orderId, user_id: userId, product, amount, tx_id: payment.tx_id },
      'order created',
    );

    res.status(201).json({
      order_id: orderId,
      user_id: userId,
      product,
      amount,
      payment,
      created_at: new Date().toISOString(),
    });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
