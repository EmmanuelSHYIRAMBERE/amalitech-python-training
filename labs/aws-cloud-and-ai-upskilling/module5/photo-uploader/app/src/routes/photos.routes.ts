import { Router } from 'express';
import { getAll, create } from '../controllers/photos.controller';
import { uploadPhotoMiddleware } from '../middleware/upload.middleware';

const router = Router();

router.get('/', getAll);
router.post('/', uploadPhotoMiddleware, create);

export default router;
