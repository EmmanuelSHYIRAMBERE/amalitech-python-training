"""S3 upload + CloudFront URL builder -- replicates
src/services/s3.service.ts directly via boto3 (no django-storages
abstraction, matching the Node app's direct @aws-sdk/client-s3 usage)."""

from __future__ import annotations

import uuid

import boto3
from django.conf import settings

_s3_client = boto3.client("s3", region_name=settings.AWS_REGION)


def upload_photo(file_bytes: bytes, mime_type: str, original_name: str) -> str:
    """Uploads a photo to S3 under photos/{uuid4}.{ext}. Returns the S3 key."""
    ext = original_name.rsplit(".", 1)[-1] if "." in original_name else "jpg"
    key = f"photos/{uuid.uuid4()}.{ext}"

    _s3_client.put_object(
        Bucket=settings.PHOTOS_BUCKET,
        Key=key,
        Body=file_bytes,
        ContentType=mime_type,
    )
    return key


def photo_url(s3_key: str) -> str:
    """Builds the public CloudFront URL for a given S3 key (plain concat,
    no signing -- identical to s3.service.ts's photoUrl())."""
    return f"https://{settings.CLOUDFRONT_DOMAIN}/{s3_key}"
