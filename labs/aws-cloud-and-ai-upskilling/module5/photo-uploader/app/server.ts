import http from 'http';
import dotenv from 'dotenv';

dotenv.config();

import app from './app';
import { closePool } from './src/db/pool';

const PORT = process.env.PORT || 3000;

const httpServer = http.createServer(app);

const start = (): void => {
  httpServer.listen(PORT, () => {
    console.log(`[Photo Uploader] Server running on http://localhost:${PORT}`);
    console.log(`[Photo Uploader] Health check at http://localhost:${PORT}/health`);
  });
};

httpServer.on('error', (err) => {
  console.error(`[Server] Failed to start: ${err.message}`);
  process.exit(1);
});

const shutdown = (signal: string): void => {
  console.log(`[Server] ${signal} received — shutting down gracefully`);
  httpServer.close(async () => {
    await closePool();
    console.log('[Server] HTTP server closed');
    process.exit(0);
  });
};

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));

start();
