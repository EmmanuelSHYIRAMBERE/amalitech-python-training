import { NextFunction, Request, Response, Router } from 'express';
import photosRoutes from './photos.routes';
import ErrorHandler from '../utils/errorhandler.utility';
import { globalErrorController } from '../controllers/error.controller';

const routes = Router();

routes.use('/api/v1/photos', photosRoutes);

routes.all('/{0,}', (req: Request, _res: Response, next: NextFunction) => {
  next(new ErrorHandler({ message: `Route ${req.originalUrl} not found`, statusCode: 404 }));
});

routes.use(globalErrorController);

export default routes;
