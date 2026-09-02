/**
 * @fileoverview Express application factory for the ECR Lab API.
 *
 * Configures and exports the Express app instance with:
 *  - CORS middleware (open for lab purposes)
 *  - JSON and URL-encoded body parsers
 *  - Health check endpoint used by Docker HEALTHCHECK and load balancers
 *  - Root info endpoint
 *  - All API v1 routes (mounted via src/routes/index.ts)
 *
 * The app is intentionally kept separate from the HTTP server (server.ts)
 * to make it independently testable without binding to a port.
 */
import express from 'express';
import cors from 'cors';
import routes from './src/routes';

const app = express();

/**
 * CORS — allows all origins for this lab.
 * In production, restrict `origin` to known client domains.
 */
app.use(
  cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'Accept'],
  })
);

// Parse incoming JSON bodies (max 10 MB)
app.use(express.json({ limit: '10mb' }));
// Parse URL-encoded form bodies (max 10 MB)
app.use(express.urlencoded({ extended: false, limit: '10mb' }));

/**
 * GET /health
 *
 * Health check endpoint consumed by:
 *  - Docker HEALTHCHECK instruction in the Dockerfile
 *  - AWS ECS/ALB target group health checks
 *
 * Returns 200 with environment and timestamp so you can confirm
 * which build/environment is running.
 */
app.get('/health', (_req, res) => {
  res.status(200).json({
    success: true,
    message: 'ECR Lab API is healthy',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString(),
  });
});

/**
 * GET /
 *
 * Root endpoint — returns basic API metadata.
 * Useful for a quick sanity check after deployment.
 */
app.get('/', (_req, res) => {
  res.status(200).json({
    success: true,
    message: 'ECR Lab API — Emmanuel Shyirambere',
    version: '1.0.1',
  });
});

// Mount all versioned API routes (includes 404 handler and global error handler)
app.use('/', routes);

export default app;
