import { NextFunction, Request, Response } from 'express';

interface ErrorArgs {
  message: string;
  statusCode: number;
}

export default class ErrorHandler extends Error {
  statusCode: number;
  status: string;
  isOperational: boolean;

  constructor({ message, statusCode }: ErrorArgs) {
    super(message);
    this.statusCode = statusCode;
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

type AsyncFunction = (req: Request, res: Response, next: NextFunction) => Promise<void>;

export const catchAsyncError = (asyncFunction: AsyncFunction) => {
  return (req: Request, res: Response, next: NextFunction) => {
    asyncFunction(req, res, next).catch(next);
  };
};
