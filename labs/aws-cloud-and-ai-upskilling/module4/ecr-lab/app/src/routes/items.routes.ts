/**
 * @fileoverview Route definitions for the /api/v1/items resource.
 *
 * Each route applies Zod validation middleware before the controller
 * so invalid payloads are rejected with a 400 before hitting business logic.
 *
 * Routes:
 *  GET    /api/v1/items       — list all items
 *  GET    /api/v1/items/:id   — get a single item by UUID
 *  POST   /api/v1/items       — create a new item
 *  PATCH  /api/v1/items/:id   — partially update an item
 *  DELETE /api/v1/items/:id   — delete an item
 */
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
