import { Pool } from 'pg';
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';

let pool: Pool | null = null;

interface DbSecret {
  username: string;
  password: string;
}

/**
 * Resolves the DB password: reads it from AWS Secrets Manager if
 * DB_SECRET_ARN is set (production/ECS), otherwise falls back to
 * DB_PASSWORD from the environment (local development).
 */
const resolvePassword = async (): Promise<string> => {
  const secretArn = process.env.DB_SECRET_ARN;
  if (!secretArn) {
    return process.env.DB_PASSWORD || '';
  }

  const client = new SecretsManagerClient({ region: process.env.AWS_REGION || 'eu-north-1' });
  const response = await client.send(new GetSecretValueCommand({ SecretId: secretArn }));
  const secret: DbSecret = JSON.parse(response.SecretString || '{}');
  return secret.password;
};

/**
 * Lazily creates and returns the shared pg connection pool, resolving
 * the password from Secrets Manager on first use.
 */
export const getPool = async (): Promise<Pool> => {
  if (pool) return pool;

  const password = await resolvePassword();

  // RDS requires SSL; a plain local Postgres container (no DB_SECRET_ARN
  // set) typically doesn't support it, so only enable it against RDS.
  const useSsl = Boolean(process.env.DB_SECRET_ARN);

  pool = new Pool({
    host: process.env.DB_HOST,
    port: Number(process.env.DB_PORT || 5432),
    database: process.env.DB_NAME || 'photouploader',
    user: process.env.DB_USER || 'photoapp',
    password,
    max: 5,
    ssl: useSsl ? { rejectUnauthorized: false } : false,
  });

  return pool;
};

export const closePool = async (): Promise<void> => {
  if (pool) {
    await pool.end();
    pool = null;
  }
};
