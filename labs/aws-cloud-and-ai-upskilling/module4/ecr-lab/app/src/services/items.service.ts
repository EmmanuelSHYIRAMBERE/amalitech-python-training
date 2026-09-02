/**
 * @fileoverview In-memory data store and CRUD operations for the Item resource.
 *
 * Uses a Map keyed by UUID as the backing store. This avoids any external
 * database dependency, keeping the app self-contained for the containerization
 * lab. Data is lost on container restart — intentional for this lab scope.
 *
 * All functions throw an operational ErrorHandler (not a raw Error) so the
 * global error controller can return the correct HTTP status code.
 */
import { randomUUID } from 'crypto';
import ErrorHandler from '../utils/errorhandler.utility';
import { CreateItemInput, UpdateItemInput } from '../validations/items.validation';

/** Shape of a stored item. */
export interface Item {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * In-memory store — no external DB required for this containerization lab.
 * Key: item UUID, Value: Item object.
 */
const store = new Map<string, Item>();

/**
 * Returns all items as an array.
 * Returns an empty array when the store is empty.
 */
export const getAllItems = (): Item[] => Array.from(store.values());

/**
 * Finds and returns a single item by its UUID.
 *
 * @param id - The UUID of the item to retrieve
 * @throws {ErrorHandler} 404 if no item with the given id exists
 */
export const getItemById = (id: string): Item => {
  const item = store.get(id);
  if (!item) throw new ErrorHandler({ message: `Item with id "${id}" not found`, statusCode: 404 });
  return item;
};

/**
 * Creates a new item, assigns a UUID and timestamps, and persists it.
 *
 * @param input - Validated create payload (name, optional description)
 * @returns The newly created item including its generated id
 */
export const createItem = (input: CreateItemInput): Item => {
  const now = new Date().toISOString();
  const item: Item = { id: randomUUID(), ...input, createdAt: now, updatedAt: now };
  store.set(item.id, item);
  return item;
};

/**
 * Partially updates an existing item by merging the input over the stored value.
 * Only fields present in `input` are changed; all other fields are preserved.
 *
 * @param id    - The UUID of the item to update
 * @param input - Validated partial update payload
 * @throws {ErrorHandler} 404 if no item with the given id exists
 */
export const updateItem = (id: string, input: UpdateItemInput): Item => {
  const existing = getItemById(id);
  const updated: Item = { ...existing, ...input, updatedAt: new Date().toISOString() };
  store.set(id, updated);
  return updated;
};

/**
 * Removes an item from the store by its UUID.
 *
 * @param id - The UUID of the item to delete
 * @throws {ErrorHandler} 404 if no item with the given id exists
 */
export const deleteItem = (id: string): void => {
  getItemById(id); // throws 404 if not found
  store.delete(id);
};
