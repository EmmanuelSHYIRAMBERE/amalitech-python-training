import { getPool } from './pool';

/**
 * Creates the photos table if it doesn't already exist. Called once at
 * startup — idempotent, safe to run on every container start.
 */
export const ensureSchema = async (): Promise<void> => {
  const pool = await getPool();
  await pool.query('CREATE EXTENSION IF NOT EXISTS pgcrypto');
  await pool.query(`
    CREATE TABLE IF NOT EXISTS photos (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      s3_key TEXT NOT NULL,
      description TEXT NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
  `);
};
