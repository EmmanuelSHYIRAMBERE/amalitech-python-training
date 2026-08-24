/**
 * @fileoverview HTTP request handlers for the /api/v1/items resource.
 *
 * Each controller function:
 *  1. Delegates all business logic to the items service
 *  2. Formats and sends the HTTP response
 *  3. Forwards any thrown error to the global error handler via next(error)
 *
 * Validation is handled upstream by the validate middleware, so controllers
 * can safely assume req.body is already a valid, typed payload.
 */
import { Request, Response, NextFunction } from 'express';
import * as itemsService from '../services/items.service';

/**
 * GET /api/v1/items
 *
 * Returns all items currently held in the in-memory store.
 * Responds with an empty array when no items exist.
 */
export const getAll = async (_req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const items = itemsService.getAllItems();
    res.status(200).json({ success: true, data: items });
  } catch (error) {
    next(error);
  }
};

/**
 * GET /api/v1/items/:id
 *
 * Returns a single item by its UUID.
 * The service throws a 404 ErrorHandler if the id does not exist.
 */
export const getOne = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const item = itemsService.getItemById(req.params.id as string);
    res.status(200).json({ success: true, data: item });
  } catch (error) {
    next(error);
  }
};

/**
 * POST /api/v1/items
 *
 * Creates a new item from the validated request body.
 * Responds with 201 and the newly created item including its generated UUID.
 */
export const create = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const item = itemsService.createItem(req.body);
    res.status(201).json({ success: true, message: 'Item created', data: item });
  } catch (error) {
    next(error);
  }
};

/**
 * PATCH /api/v1/items/:id
 *
 * Partially updates an existing item.
 * Only fields present in the request body are updated; others are preserved.
 * The service throws a 404 ErrorHandler if the id does not exist.
 */
export const update = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const item = itemsService.updateItem(req.params.id as string, req.body);
    res.status(200).json({ success: true, message: 'Item updated', data: item });
  } catch (error) {
    next(error);
  }
};

/**
 * DELETE /api/v1/items/:id
 *
 * Removes an item from the store by its UUID.
 * The service throws a 404 ErrorHandler if the id does not exist.
 */
export const remove = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    itemsService.deleteItem(req.params.id as string);
    res.status(200).json({ success: true, message: 'Item deleted' });
  } catch (error) {
    next(error);
  }
};
