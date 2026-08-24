import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';

export const validate = (schema: ZodSchema) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (err) {
      if (err instanceof ZodError) {
        res.status(400).json({
          success: false,
          statusCode: 400,
          message: err.errors.map((e) => `${e.path.join('.')}: ${e.message}`).join(', '),
        });
        return;
      }
      next(err);
    }
  };
};
