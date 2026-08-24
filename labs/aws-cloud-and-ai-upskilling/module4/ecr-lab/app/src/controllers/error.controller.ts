/**
 * @fileoverview Global Express error handler.
 *
 * This controller must be registered LAST in the middleware chain and must
 * declare exactly 4 parameters so Express recognises it as an error handler.
 *
 * Handles all errors forwarded via next(error) from any route or middleware,
 * normalises the status code and status string, logs the message, and sends
 * a consistent JSON error response to the client.
 */
import { NextFunction, Request, Response } from 'express';
import ErrorHandler from '../utils/errorhandler.utility';

/**
 * Centralized error handler middleware.
 *
 * @param err   - Any error object (operational ErrorHandler or unexpected Error)
 * @param _req  - Express request (unused)
 * @param res   - Express response used to send the error JSON
 * @param _next - Express next function (required by Express error handler signature)
 */
export const globalErrorController = (
  err: any,
  _req: Request,
  res: Response,
  _next: NextFunction
) => {
  // Default to 500 if no status code was set on the error
  err.statusCode = err.statusCode || 500;
  err.status = err.status || 'error';

  console.error('[Error]', err.message);

  res.status(err.statusCode).json({
    success: false,
    statusCode: err.statusCode,
    message: err.message,
  });
};
