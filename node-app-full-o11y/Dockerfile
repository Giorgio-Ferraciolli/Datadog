# syntax=docker/dockerfile:1.7

# =============================================================================
# Stage 1 — build: install production dependencies with full toolchain available
# (dd-trace and its profiler have native addons that compile on first install).
# =============================================================================
FROM node:20-bookworm-slim AS build

WORKDIR /app

# Tooling needed to compile native modules used by dd-trace's profiler.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        make \
        g++ \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY package.json ./
# package-lock.json is optional; copy it only if present without failing.
COPY package-lock.json* ./

# Install only production deps. `npm ci` is preferred when a lockfile exists,
# falling back to `npm install` otherwise.
RUN if [ -f package-lock.json ]; then \
        npm ci --omit=dev --no-audit --no-fund; \
    else \
        npm install --omit=dev --no-audit --no-fund; \
    fi

# =============================================================================
# Stage 2 — runtime: slim image, non-root user, only what's needed to run.
# =============================================================================
FROM node:20-bookworm-slim AS runtime

ENV NODE_ENV=production \
    NPM_CONFIG_LOGLEVEL=warn

WORKDIR /app

# Copy installed node_modules from the build stage.
COPY --from=build /app/node_modules ./node_modules

# Copy application source.
COPY package.json ./
COPY src ./src

# Drop privileges — the official node image ships with a `node` user (uid 1000).
RUN chown -R node:node /app
USER node

EXPOSE 3000

# tracer.js is the only valid entry point — it initializes dd-trace before
# requiring the rest of the app.
CMD ["node", "src/tracer.js"]
