import { randomUUID } from 'crypto';
import ErrorHandler from '../utils/errorhandler.utility';
import { CreateItemInput, UpdateItemInput } from '../validations/items.validation';

export interface Item {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

// In-memory store — no external DB required for this containerization lab
const store = new Map<string, Item>();

export const getAllItems = (): Item[] => Array.from(store.values());

export const getItemById = (id: string): Item => {
  const item = store.get(id);
  if (!item) throw new ErrorHandler({ message: `Item with id "${id}" not found`, statusCode: 404 });
  return item;
};

export const createItem = (input: CreateItemInput): Item => {
  const now = new Date().toISOString();
  const item: Item = { id: randomUUID(), ...input, createdAt: now, updatedAt: now };
  store.set(item.id, item);
  return item;
};

export const updateItem = (id: string, input: UpdateItemInput): Item => {
  const existing = getItemById(id);
  const updated: Item = { ...existing, ...input, updatedAt: new Date().toISOString() };
  store.set(id, updated);
  return updated;
};

export const deleteItem = (id: string): void => {
  getItemById(id); // throws 404 if not found
  store.delete(id);
};
