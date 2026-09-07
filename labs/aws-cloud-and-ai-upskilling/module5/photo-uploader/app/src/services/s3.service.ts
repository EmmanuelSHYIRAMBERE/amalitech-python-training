import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { randomUUID } from 'crypto';

const s3 = new S3Client({ region: process.env.AWS_REGION || 'eu-north-1' });

const BUCKET = process.env.PHOTOS_BUCKET as string;

/**
 * Uploads a photo buffer to S3 under a random UUID key, preserving the
 * original file extension. Returns the S3 object key.
 */
export const uploadPhoto = async (buffer: Buffer, mimeType: string, originalName: string): Promise<string> => {
  const ext = originalName.includes('.') ? originalName.split('.').pop() : 'jpg';
  const key = `photos/${randomUUID()}.${ext}`;

  await s3.send(
    new PutObjectCommand({
      Bucket: BUCKET,
      Key: key,
      Body: buffer,
      ContentType: mimeType,
    })
  );

  return key;
};

/**
 * Builds the public-facing CloudFront URL for a given S3 key.
 */
export const photoUrl = (s3Key: string): string => {
  const domain = process.env.CLOUDFRONT_DOMAIN;
  return `https://${domain}/${s3Key}`;
};
