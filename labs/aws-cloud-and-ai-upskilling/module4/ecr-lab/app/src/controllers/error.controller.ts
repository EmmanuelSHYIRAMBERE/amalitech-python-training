import { NextFunction, Request, Response } from 'express';
import ErrorHandler from '../utils/errorhandler.utility';

export const globalErrorController = (
  err: any,
  _req: Request,
  res: Response,
  _next: NextFunction
) => {
  err.statusCode = err.statusCode || 500;
  err.status = err.status || 'error';

  console.error('[Error]', err.message);

  res.status(err.statusCode).json({
    success: false,
    statusCode: err.statusCode,
    message: err.message,
  });
};
