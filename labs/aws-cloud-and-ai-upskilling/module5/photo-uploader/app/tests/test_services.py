from unittest.mock import patch

from photos.services import photo_url, upload_photo


@patch("photos.services._s3_client")
def test_upload_photo_builds_key_and_calls_put_object(mock_s3_client, settings):
    settings.PHOTOS_BUCKET = "test-bucket"

    key = upload_photo(b"fake-bytes", "image/jpeg", "myphoto.jpg")

    assert key.startswith("photos/")
    assert key.endswith(".jpg")

    mock_s3_client.put_object.assert_called_once()
    call_kwargs = mock_s3_client.put_object.call_args.kwargs
    assert call_kwargs["Bucket"] == "test-bucket"
    assert call_kwargs["Key"] == key
    assert call_kwargs["Body"] == b"fake-bytes"
    assert call_kwargs["ContentType"] == "image/jpeg"


@patch("photos.services._s3_client")
def test_upload_photo_defaults_extension_when_no_dot(mock_s3_client, settings):
    settings.PHOTOS_BUCKET = "test-bucket"

    key = upload_photo(b"fake-bytes", "image/jpeg", "noextension")

    assert key.endswith(".jpg")


def test_photo_url_builds_cloudfront_url(settings):
    settings.CLOUDFRONT_DOMAIN = "abc123.cloudfront.net"
    assert photo_url("photos/foo.jpg") == "https://abc123.cloudfront.net/photos/foo.jpg"
