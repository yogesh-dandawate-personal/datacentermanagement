"""
S3/MinIO Integration Client

Supports both AWS S3 and MinIO object storage with:
- Upload/download operations
- Presigned URL generation
- File hash verification
- Tenant isolation
- Error handling and retries
"""

import os
import logging
import hashlib
from typing import Optional, BinaryIO, Tuple
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from io import BytesIO

logger = logging.getLogger(__name__)


class S3ClientError(Exception):
    """Custom exception for S3 operations"""
    pass


class S3Client:
    """
    S3/MinIO client wrapper for iNetZero Evidence Repository

    Supports:
    - AWS S3
    - MinIO (S3-compatible)
    - Presigned URLs
    - SHA256 verification
    - Automatic bucket creation
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
    ):
        """
        Initialize S3 client

        Args:
            bucket_name: S3 bucket name (defaults to env var)
            region: AWS region (defaults to env var, ignored for MinIO)
            endpoint_url: MinIO endpoint URL (optional)
            access_key_id: AWS/MinIO access key
            secret_access_key: AWS/MinIO secret key
        """
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "evidence-repository")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.endpoint_url = endpoint_url or os.getenv("MINIO_ENDPOINT_URL")
        self.is_minio = bool(self.endpoint_url)

        # Get credentials
        self.access_key_id = access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_access_key = secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")

        # Initialize S3 client
        self.client = self._initialize_client()

        logger.info(
            f"S3Client initialized: bucket={self.bucket_name}, "
            f"type={'MinIO' if self.is_minio else 'AWS S3'}"
        )

    def _initialize_client(self):
        """Initialize boto3 S3 client"""
        try:
            config = {}
            if self.is_minio:
                config["signature_version"] = "s3v4"

            s3_client = boto3.client(
                "s3",
                region_name=self.region if not self.is_minio else None,
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
            )

            # Test connection and create bucket if needed
            self._ensure_bucket_exists(s3_client)
            return s3_client

        except (NoCredentialsError, PartialCredentialsError) as e:
            logger.warning(f"S3 credentials not configured: {str(e)}")
            logger.warning("S3 operations will fail until credentials are configured")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise S3ClientError(f"Failed to initialize S3 client: {str(e)}")

    def _ensure_bucket_exists(self, client):
        """Create bucket if it doesn't exist"""
        try:
            client.head_bucket(Bucket=self.bucket_name)
            logger.debug(f"Bucket {self.bucket_name} exists")
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                try:
                    if self.is_minio or self.region == "us-east-1":
                        client.create_bucket(Bucket=self.bucket_name)
                    else:
                        client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={"LocationConstraint": self.region},
                        )
                    logger.info(f"Created bucket: {self.bucket_name}")
                except ClientError as create_error:
                    logger.warning(f"Could not create bucket: {create_error}")
            else:
                raise

    def upload_file(
        self,
        file_content: BinaryIO,
        tenant_id: str,
        document_name: str,
        metadata: Optional[dict] = None,
    ) -> Tuple[str, str, int]:
        """
        Upload a file to S3/MinIO

        Args:
            file_content: Binary file content
            tenant_id: Tenant ID for isolation
            document_name: Original document name
            metadata: Optional metadata dict

        Returns:
            Tuple of (document_key, file_hash, file_size_bytes)

        Raises:
            S3ClientError: If upload fails
        """
        if not self.client:
            raise S3ClientError("S3 client not initialized")

        try:
            # Read file content and calculate hash
            file_bytes = file_content.read()
            file_hash = self._calculate_sha256(file_bytes)
            file_size = len(file_bytes)

            # Generate object key with tenant isolation
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            document_key = f"tenants/{tenant_id}/evidence/{timestamp}_{document_name}"

            # Prepare metadata
            extra_args = {
                "Metadata": {
                    "tenant_id": tenant_id,
                    "upload_time": datetime.utcnow().isoformat(),
                    "original_name": document_name,
                }
            }

            if metadata:
                extra_args["Metadata"].update(metadata)

            # Upload file
            logger.info(f"Uploading file: {document_key} (size: {file_size} bytes)")
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=document_key,
                Body=BytesIO(file_bytes),
                ContentLength=file_size,
                Metadata=extra_args["Metadata"],
            )

            logger.info(f"Successfully uploaded {document_key}")
            return document_key, file_hash, file_size

        except ClientError as e:
            error_msg = f"Failed to upload file: {str(e)}"
            logger.error(error_msg)
            raise S3ClientError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during upload: {str(e)}"
            logger.error(error_msg)
            raise S3ClientError(error_msg)

    def download_file(self, document_key: str) -> BinaryIO:
        """
        Download a file from S3/MinIO

        Args:
            document_key: S3 object key

        Returns:
            File content as BinaryIO

        Raises:
            S3ClientError: If download fails
        """
        if not self.client:
            raise S3ClientError("S3 client not initialized")

        try:
            logger.info(f"Downloading file: {document_key}")
            response = self.client.get_object(Bucket=self.bucket_name, Key=document_key)
            file_content = BytesIO(response["Body"].read())
            file_content.seek(0)
            logger.info(f"Successfully downloaded {document_key}")
            return file_content

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise S3ClientError(f"File not found: {document_key}")
            else:
                raise S3ClientError(f"Failed to download file: {str(e)}")
        except Exception as e:
            error_msg = f"Unexpected error during download: {str(e)}"
            logger.error(error_msg)
            raise S3ClientError(error_msg)

    def get_presigned_url(
        self,
        document_key: str,
        expires_in_seconds: int = 3600,
    ) -> str:
        """
        Generate a presigned URL for secure file access

        Args:
            document_key: S3 object key
            expires_in_seconds: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL string

        Raises:
            S3ClientError: If URL generation fails
        """
        if not self.client:
            raise S3ClientError("S3 client not initialized")

        try:
            logger.info(f"Generating presigned URL for: {document_key}")
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": document_key},
                ExpiresIn=expires_in_seconds,
            )
            logger.info(f"Successfully generated presigned URL (expires in {expires_in_seconds}s)")
            return url

        except ClientError as e:
            error_msg = f"Failed to generate presigned URL: {str(e)}"
            logger.error(error_msg)
            raise S3ClientError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error generating presigned URL: {str(e)}"
            logger.error(error_msg)
            raise S3ClientError(error_msg)

    def delete_file(self, document_key: str) -> bool:
        """
        Delete a file from S3/MinIO

        Args:
            document_key: S3 object key

        Returns:
            True if deletion successful, False otherwise

        Raises:
            S3ClientError: If deletion fails
        """
        if not self.client:
            raise S3ClientError("S3 client not initialized")

        try:
            logger.info(f"Deleting file: {document_key}")
            self.client.delete_object(Bucket=self.bucket_name, Key=document_key)
            logger.info(f"Successfully deleted {document_key}")
            return True

        except ClientError as e:
            error_msg = f"Failed to delete file: {str(e)}"
            logger.error(error_msg)
            raise S3ClientError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during deletion: {str(e)}"
            logger.error(error_msg)
            raise S3ClientError(error_msg)

    def verify_file_integrity(
        self,
        document_key: str,
        expected_hash: str,
    ) -> bool:
        """
        Verify file integrity using SHA256 hash

        Args:
            document_key: S3 object key
            expected_hash: Expected SHA256 hash

        Returns:
            True if hash matches, False otherwise

        Raises:
            S3ClientError: If verification fails
        """
        try:
            logger.info(f"Verifying integrity of: {document_key}")
            file_content = self.download_file(document_key)
            actual_hash = self._calculate_sha256(file_content.read())

            if actual_hash.lower() == expected_hash.lower():
                logger.info(f"Integrity verified for {document_key}")
                return True
            else:
                logger.warning(
                    f"Hash mismatch for {document_key}: "
                    f"expected={expected_hash}, actual={actual_hash}"
                )
                return False

        except S3ClientError:
            raise
        except Exception as e:
            error_msg = f"Error verifying file integrity: {str(e)}"
            logger.error(error_msg)
            raise S3ClientError(error_msg)

    @staticmethod
    def _calculate_sha256(file_content: bytes) -> str:
        """
        Calculate SHA256 hash of file content

        Args:
            file_content: File bytes

        Returns:
            Hex-encoded SHA256 hash
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_content)
        return sha256_hash.hexdigest()

    def is_healthy(self) -> bool:
        """Check if S3 client is healthy and can connect"""
        if not self.client:
            return False

        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except Exception as e:
            logger.error(f"S3 health check failed: {str(e)}")
            return False


# Singleton instance for application use
_s3_client: Optional[S3Client] = None


def get_s3_client() -> S3Client:
    """Get or create the S3 client singleton"""
    global _s3_client
    if _s3_client is None:
        _s3_client = S3Client()
    return _s3_client
