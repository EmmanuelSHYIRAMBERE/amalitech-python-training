import { Router } from 'express';
import { getAll, getOne, create, update, remove } from '../controllers/items.controller';
import { validate } from '../middleware/validate.middleware';
import { createItemSchema, updateItemSchema } from '../validations/items.validation';

const router = Router();

router.get('/', getAll);
router.get('/:id', getOne);
router.post('/', validate(createItemSchema), create);
router.patch('/:id', validate(updateItemSchema), update);
router.delete('/:id', remove);

export default router;
