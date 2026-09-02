/**
 * @fileoverview Central route registry for the ECR Lab API.
 *
 * Mounts all resource route groups under /api/v1 and appends:
 *  - A 404 catch-all for unmatched routes
 *  - The global error handler (must be registered last with 4 arguments)
 */
import { NextFunction, Request, Response, Router } from 'express';
import itemsRoutes from './items.routes';
import ErrorHandler from '../utils/errorhandler.utility';
import { globalErrorController } from '../controllers/error.controller';

const routes = Router();

// ----------------------------------------------------------------
// API v1 route groups
// ----------------------------------------------------------------
routes.use('/api/v1/items', itemsRoutes);

// ----------------------------------------------------------------
// 404 — catches any request that matched none of the routes above
// ----------------------------------------------------------------
routes.all('/{0,}', (req: Request, _res: Response, next: NextFunction) => {
  next(new ErrorHandler({ message: `Route ${req.originalUrl} not found`, statusCode: 404 }));
});

// Global error handler — must be last, must have 4 arguments
routes.use(globalErrorController);

export default routes;
