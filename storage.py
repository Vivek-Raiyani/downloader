import boto3
import os
import logging
from botocore.exceptions import NoCredentialsError
from config import settings

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self):
        self.s3_enabled = settings.S3_ENABLED
        if self.s3_enabled:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.S3_REGION
            )
            self.bucket_name = settings.S3_BUCKET_NAME

    def upload_file(self, local_filepath: str, object_name: str = None) -> str | None:
        """
        Uploads a file to S3 if enabled. Returns the S3 URL or None.
        """
        if not self.s3_enabled:
            return None

        if object_name is None:
            object_name = os.path.basename(local_filepath)

        try:
            self.s3_client.upload_file(local_filepath, self.bucket_name, object_name)
            s3_url = f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{object_name}"
            logger.info(f"File uploaded to S3: {s3_url}")
            return s3_url
        except FileNotFoundError:
            logger.error("The file was not found")
            return None
        except NoCredentialsError:
            logger.error("Credentials not available")
            return None
        except Exception as e:
            logger.error(f"S3 Upload failed: {str(e)}")
            return None

    def delete_local_file(self, filepath: str):
        """
        Deletes the local file after S3 upload.
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Local file deleted: {filepath}")
        except Exception as e:
            logger.error(f"Failed to delete local file: {str(e)}")

    def cleanup_old_files(self):
        """
        Deletes files in the download directory that are older than FILE_RETENTION_SECONDS.
        """
        import time
        now = time.time()
        retention = settings.FILE_RETENTION_SECONDS
        count = 0

        print(f"\n[CLEANUP] Scanning for files older than {retention} seconds...")
        logger.info(f"Starting cleanup of files older than {retention} seconds...")
        
        try:
            if not os.path.exists(settings.DOWNLOAD_DIR):
                print(f"[CLEANUP] Directory {settings.DOWNLOAD_DIR} not found.")
                return

            files = os.listdir(settings.DOWNLOAD_DIR)
            print(f"[CLEANUP] Found {len(files)} files in directory.")

            for filename in files:
                filepath = os.path.join(settings.DOWNLOAD_DIR, filename)
                
                # Skip directories
                if os.path.isdir(filepath):
                    continue
                
                # Check file age
                file_age = now - os.path.getmtime(filepath)
                print(f"[CLEANUP] Checking {filename}: Age={int(file_age)}s")
                
                if file_age > retention:
                    os.remove(filepath)
                    print(f"[CLEANUP] DELETED: {filename}")
                    logger.info(f"Cleaned up old file: {filename}")
                    count += 1
            
            if count > 0:
                print(f"[CLEANUP] Finished. Removed {count} files.")
                logger.info(f"Cleanup finished. Removed {count} files.")
            else:
                print("[CLEANUP] No files were eligible for deletion.")
        except Exception as e:
            print(f"[CLEANUP] ERROR: {str(e)}")
            logger.error(f"Error during cleanup: {str(e)}")

storage_manager = StorageManager()
