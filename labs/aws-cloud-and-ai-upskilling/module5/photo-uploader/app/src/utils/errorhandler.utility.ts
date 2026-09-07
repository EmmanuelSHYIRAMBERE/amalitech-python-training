interface ErrorArgs {
  message: string;
  statusCode: number;
}

/**
 * Operational error with an HTTP status code, thrown by services/
 * controllers for expected failure cases (e.g. missing file, bad input).
 */
export default class ErrorHandler extends Error {
  statusCode: number;
  status: string;

  constructor({ message, statusCode }: ErrorArgs) {
    super(message);
    this.statusCode = statusCode;
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
    Error.captureStackTrace(this, this.constructor);
  }
}
