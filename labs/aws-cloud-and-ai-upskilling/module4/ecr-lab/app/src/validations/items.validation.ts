/**
 * @fileoverview Zod validation schemas for the Item resource.
 *
 * Defines two schemas:
 *  - `createItemSchema` — used on POST /api/v1/items (name required)
 *  - `updateItemSchema` — used on PATCH /api/v1/items/:id (all fields optional)
 *
 * Inferred TypeScript types are exported alongside the schemas so controllers
 * and services share the same type definitions without duplication.
 */
import { z } from 'zod';

/**
 * Schema for creating a new item.
 * - `name` is required, 1–100 characters
 * - `description` is optional, max 500 characters
 */
export const createItemSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  description: z.string().max(500).optional(),
});

/**
 * Schema for partially updating an existing item.
 * All fields are optional — only provided fields will be updated.
 */
export const updateItemSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  description: z.string().max(500).optional(),
});

/** TypeScript type inferred from createItemSchema */
export type CreateItemInput = z.infer<typeof createItemSchema>;
/** TypeScript type inferred from updateItemSchema */
export type UpdateItemInput = z.infer<typeof updateItemSchema>;
