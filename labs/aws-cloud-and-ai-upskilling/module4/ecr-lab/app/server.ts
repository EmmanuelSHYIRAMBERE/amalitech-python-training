/**
 * @fileoverview HTTP server entry point for the ECR Lab API.
 *
 * Responsibilities:
 *  - Loads environment variables from .env before any other import
 *  - Creates a raw Node.js HTTP server wrapping the Express app
 *  - Starts listening on the configured PORT
 *  - Handles OS signals (SIGINT, SIGTERM) for graceful shutdown so that
 *    in-flight requests are completed before the process exits — critical
 *    when running inside a Docker container on ECS/Fargate
 */
import http from "http";
import dotenv from "dotenv";

// Load .env before importing app so process.env is populated for all modules
dotenv.config();

import app from "./app";

const PORT = process.env.PORT || 3000;

/** Wraps the Express app in a plain Node.js HTTP server for full control over lifecycle. */
const httpServer = http.createServer(app);

/**
 * Starts the HTTP server and begins accepting connections.
 * Logs the base URL and health check endpoint for quick verification.
 */
const start = (): void => {
  httpServer.listen(PORT, () => {
    console.log(
      `[ECR Lab] Server running on http://localhost:${PORT} updated today`,
    );
    console.log(`[ECR Lab] Health check at http://localhost:${PORT}/health`);
  });
};

/**
 * Handles fatal server startup errors (e.g. port already in use).
 * Exits with code 1 so Docker/ECS knows the container failed to start.
 */
httpServer.on("error", (err) => {
  console.error(`[Server] Failed to start: ${err.message}`);
  process.exit(1);
});

/**
 * Gracefully shuts down the HTTP server on the given OS signal.
 *
 * Stops accepting new connections, waits for existing ones to finish,
 * then exits cleanly. Docker sends SIGTERM before force-killing a container,
 * so this ensures zero dropped requests during deployments.
 *
 * @param signal - The OS signal name (e.g. 'SIGINT', 'SIGTERM')
 */
const shutdown = (signal: string): void => {
  console.log(`[Server] ${signal} received — shutting down gracefully`);
  httpServer.close(() => {
    console.log("[Server] HTTP server closed");
    process.exit(0);
  });
};

// Ctrl+C in local development
process.on("SIGINT", () => shutdown("SIGINT"));
// Docker stop / ECS task termination
process.on("SIGTERM", () => shutdown("SIGTERM"));

start();
