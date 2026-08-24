/**
 * @fileoverview Custom operational error class and async error wrapper.
 *
 * ErrorHandler extends the native Error class with HTTP-specific fields
 * (statusCode, status, isOperational) so the global error controller can
 * distinguish between expected operational errors (e.g. 404 Not Found) and
 * unexpected programmer errors (e.g. uncaught exceptions).
 *
 * catchAsyncError wraps async route handlers to automatically forward any
 * rejected promise to Express's next() without needing try/catch in every
 * controller.
 */
import { NextFunction, Request, Response } from 'express';

interface ErrorArgs {
  message: string;
  statusCode: number;
}

/**
 * Operational error with an HTTP status code.
 *
 * `isOperational = true` signals to the global error handler that this is
 * a known, expected error (e.g. resource not found, bad input) as opposed
 * to an unexpected crash.
 *
 * @example
 *   throw new ErrorHandler({ message: 'Item not found', statusCode: 404 });
 */
export default class ErrorHandler extends Error {
  statusCode: number;
  /** 'fail' for 4xx errors, 'error' for 5xx errors */
  status: string;
  /** Marks this as a known operational error, not a programmer bug */
  isOperational: boolean;

  constructor({ message, statusCode }: ErrorArgs) {
    super(message);
    this.statusCode = statusCode;
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
    this.isOperational = true;
    // Excludes the constructor itself from the stack trace
    Error.captureStackTrace(this, this.constructor);
  }
}

type AsyncFunction = (req: Request, res: Response, next: NextFunction) => Promise<void>;

/**
 * Wraps an async Express route handler so any rejected promise is
 * automatically forwarded to next() without a try/catch block.
 *
 * @param asyncFunction - An async Express handler
 * @returns A synchronous wrapper that catches and forwards errors
 *
 * @example
 *   router.get('/', catchAsyncError(async (req, res) => { ... }))
 */
export const catchAsyncError = (asyncFunction: AsyncFunction) => {
  return (req: Request, res: Response, next: NextFunction) => {
    asyncFunction(req, res, next).catch(next);
  };
};
