'use strict';

const tracer = require('dd-trace').init({
  service: process.env.DD_SERVICE || 'dd-node-monitor-app',
  env: process.env.DD_ENV || 'dev',
  version: process.env.DD_VERSION || '1.0.0',
  logInjection: true
});

const express = require('express');
const pino = require('pino');
const StatsD = require('hot-shots');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  base: {
    service: process.env.DD_SERVICE || 'dd-node-monitor-app'
  }
});

const statsd = new StatsD({
  host: process.env.DD_AGENT_HOST || 'localhost',
  port: Number(process.env.DD_DOGSTATSD_PORT || 8125),
  prefix: 'dd_node_monitor_app.',
  globalTags: {
    env: process.env.DD_ENV || 'dev'
  }
});

const app = express();
const port = Number(process.env.PORT || 3000);

app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const durationMs = Date.now() - start;
    statsd.timing('http.request_duration_ms', durationMs, [
      `method:${req.method}`,
      `route:${req.route?.path || req.path}`,
      `status:${res.statusCode}`
    ]);
    statsd.increment('http.request_count', 1, [
      `method:${req.method}`,
      `route:${req.route?.path || req.path}`,
      `status:${res.statusCode}`
    ]);
  });
  next();
});

app.get('/', (req, res) => {
  logger.info({ path: req.path }, 'Request recebida');
  res.json({
    message: 'DD Node Monitor App',
    endpoints: ['/slow', '/error', '/work']
  });
});

app.get('/slow', async (req, res) => {
  const delayMs = Number(req.query.delay || 800);
  await new Promise((resolve) => setTimeout(resolve, delayMs));
  statsd.histogram('demo.slow_endpoint_delay_ms', delayMs);
  res.json({
    message: 'Resposta lenta para teste',
    delayMs
  });
});

app.get('/error', (req, res) => {
  const error = new Error('Erro proposital para teste');
  logger.error({ err: error }, 'Falha simulada');
  statsd.increment('demo.error_count');
  res.status(500).json({
    error: error.message
  });
});

app.get('/work', (req, res) => {
  const workUnits = Number(req.query.units || 5);
  let total = 0;
  for (let i = 0; i < workUnits * 100000; i += 1) {
    total += Math.sqrt(i);
  }
  statsd.gauge('demo.work_units', workUnits);
  res.json({
    message: 'Trabalho concluído',
    workUnits,
    result: total
  });
});

app.listen(port, () => {
  logger.info(
    {
      port,
      env: process.env.DD_ENV || 'dev'
    },
    'Servidor iniciado'
  );
});

process.on('SIGTERM', () => {
  logger.info('Encerrando...');
  statsd.close();
  tracer.close();
  process.exit(0);
});