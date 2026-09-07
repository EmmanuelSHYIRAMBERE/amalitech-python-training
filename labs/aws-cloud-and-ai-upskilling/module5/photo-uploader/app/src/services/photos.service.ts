import { getPool } from '../db/pool';
import { photoUrl } from './s3.service';

export interface Photo {
  id: string;
  s3Key: string;
  description: string;
  createdAt: string;
  url: string;
}

/**
 * Returns all photos, most recent first, with their CloudFront URL
 * derived from the stored S3 key.
 */
export const getAllPhotos = async (): Promise<Photo[]> => {
  const pool = await getPool();
  const result = await pool.query(
    'SELECT id, s3_key, description, created_at FROM photos ORDER BY created_at DESC'
  );

  return result.rows.map((row) => ({
    id: row.id,
    s3Key: row.s3_key,
    description: row.description,
    createdAt: row.created_at,
    url: photoUrl(row.s3_key),
  }));
};

/**
 * Inserts a new photo record (S3 key + description) and returns it.
 */
export const createPhoto = async (s3Key: string, description: string): Promise<Photo> => {
  const pool = await getPool();
  const result = await pool.query(
    'INSERT INTO photos (s3_key, description) VALUES ($1, $2) RETURNING id, s3_key, description, created_at',
    [s3Key, description]
  );

  const row = result.rows[0];
  return {
    id: row.id,
    s3Key: row.s3_key,
    description: row.description,
    createdAt: row.created_at,
    url: photoUrl(row.s3_key),
  };
};
