import { Request, Response, NextFunction } from 'express';
import * as photosService from '../services/photos.service';
import { uploadPhoto } from '../services/s3.service';
import ErrorHandler from '../utils/errorhandler.utility';

/**
 * GET /api/v1/photos
 *
 * Returns all photos, most recent first.
 */
export const getAll = async (_req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const photos = await photosService.getAllPhotos();
    res.status(200).json({ success: true, data: photos });
  } catch (error) {
    next(error);
  }
};

/**
 * POST /api/v1/photos
 *
 * Accepts a multipart form with a "photo" file field and a
 * "description" text field. Uploads the file to S3, then records the
 * S3 key and description in Postgres.
 */
export const create = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    if (!req.file) {
      throw new ErrorHandler({ message: 'No photo file provided', statusCode: 400 });
    }

    const description = (req.body.description || '').trim();
    if (!description) {
      throw new ErrorHandler({ message: 'Description is required', statusCode: 400 });
    }

    const s3Key = await uploadPhoto(req.file.buffer, req.file.mimetype, req.file.originalname);
    const photo = await photosService.createPhoto(s3Key, description);

    res.status(201).json({ success: true, message: 'Photo uploaded', data: photo });
  } catch (error) {
    next(error);
  }
};
