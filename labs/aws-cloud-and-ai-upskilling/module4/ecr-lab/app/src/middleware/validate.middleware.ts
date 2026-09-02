/**
 * @fileoverview Zod-based request body validation middleware factory.
 *
 * Returns an Express middleware that parses and validates req.body against
 * the provided Zod schema. On success, req.body is replaced with the parsed
 * (and potentially transformed) value. On failure, responds immediately with
 * a 400 and a human-readable list of validation errors.
 *
 * Usage:
 *   router.post('/', validate(createItemSchema), controller.create)
 */
import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';

/**
 * Creates a validation middleware for the given Zod schema.
 *
 * @param schema - A Zod schema to validate req.body against
 * @returns Express middleware that validates and replaces req.body
 */
export const validate = (schema: ZodSchema) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    try {
      // Replace req.body with the parsed value so downstream handlers
      // receive a fully typed and coerced object
      req.body = schema.parse(req.body);
      next();
    } catch (err) {
      if (err instanceof ZodError) {
        // Map each Zod issue to a readable "field: message" string
        res.status(400).json({
          success: false,
          statusCode: 400,
          message: err.issues.map((e) => `${e.path.map(String).join('.')}: ${e.message}`).join(', '),
        });
        return;
      }
      // Non-Zod errors (unexpected) are forwarded to the global error handler
      next(err);
    }
  };
};
