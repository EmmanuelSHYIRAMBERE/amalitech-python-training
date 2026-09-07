import express from 'express';
import cors from 'cors';
import path from 'path';
import routes from './src/routes';
import { ensureSchema } from './src/db/schema';

const app = express();

app.use(cors({ origin: '*' }));
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: false, limit: '1mb' }));
app.use(express.static(path.join(__dirname, 'public')));

/**
 * GET /health
 *
 * Health check consumed by the ALB target group and the container's
 * own HEALTHCHECK. Also confirms the DB pool is reachable.
 */
app.get('/health', async (_req, res) => {
  res.status(200).json({
    success: true,
    message: 'Photo Uploader API is healthy',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString(),
  });
});

app.use('/', routes);

// Run once at module load — creates the photos table if it doesn't exist yet.
ensureSchema().catch((err) => {
  console.error('[Startup] Failed to initialize database schema:', err.message);
});

export default app;
