import { Request, Response, NextFunction } from 'express';
import * as itemsService from '../services/items.service';

// GET /api/v1/items
export const getAll = async (_req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const items = itemsService.getAllItems();
    res.status(200).json({ success: true, data: items });
  } catch (error) {
    next(error);
  }
};

// GET /api/v1/items/:id
export const getOne = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const item = itemsService.getItemById(req.params.id);
    res.status(200).json({ success: true, data: item });
  } catch (error) {
    next(error);
  }
};

// POST /api/v1/items
export const create = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const item = itemsService.createItem(req.body);
    res.status(201).json({ success: true, message: 'Item created', data: item });
  } catch (error) {
    next(error);
  }
};

// PATCH /api/v1/items/:id
export const update = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const item = itemsService.updateItem(req.params.id, req.body);
    res.status(200).json({ success: true, message: 'Item updated', data: item });
  } catch (error) {
    next(error);
  }
};

// DELETE /api/v1/items/:id
export const remove = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    itemsService.deleteItem(req.params.id);
    res.status(200).json({ success: true, message: 'Item deleted' });
  } catch (error) {
    next(error);
  }
};
