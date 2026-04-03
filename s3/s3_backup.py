"""
S3 Backup Manager
Author: Mustafa Talha Tuzsuz
GitHub: github.com/MustafaTuzsuz
Description: Upload local files and directories to AWS S3.
             Supports versioning, progress reporting, and error handling.
"""

import boto3
import logging
import os
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def get_s3_client():
    return boto3.client("s3")


def upload_file(local_path: str, bucket: str, s3_key: str = ""):
    """Upload a single file to S3."""
    client = get_s3_client()

    if not os.path.isfile(local_path):
        logger.error("File not found: %s", local_path)
        return False

    if not s3_key:
        s3_key = f"backups/{datetime.now().strftime('%Y-%m-%d')}/{Path(local_path).name}"

    try:
        file_size = os.path.getsize(local_path)
        logger.info("Uploading %s → s3://%s/%s (%.2f KB)",
                    local_path, bucket, s3_key, file_size / 1024)

        client.upload_file(local_path, bucket, s3_key)
        logger.info("Upload complete: s3://%s/%s", bucket, s3_key)
        return True

    except Exception as e:
        logger.error("Upload failed for %s: %s", local_path, e)
        return False


def upload_directory(local_dir: str, bucket: str, prefix: str = "backups"):
    """Recursively upload all files in a directory to S3."""
    client = get_s3_client()

    if not os.path.isdir(local_dir):
        logger.error("Directory not found: %s", local_dir)
        return

    date_prefix = datetime.now().strftime("%Y-%m-%d")
    uploaded = 0
    failed = 0

    for root, dirs, files in os.walk(local_dir):
        for filename in files:
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, local_dir)
            s3_key = f"{prefix}/{date_prefix}/{relative_path}"

            try:
                client.upload_file(local_path, bucket, s3_key)
                logger.info("Uploaded: %s → s3://%s/%s", filename, bucket, s3_key)
                uploaded += 1

            except Exception as e:
                logger.error("Failed: %s — %s", filename, e)
                failed += 1

    print(f"\n{'─'*50}")
    print(f"Backup complete — Uploaded: {uploaded} | Failed: {failed}")
    print(f"Bucket: s3://{bucket}/{prefix}/{date_prefix}/")
    print(f"{'─'*50}\n")


def list_backups(bucket: str, prefix: str = "backups"):
    """List all backup objects in S3 bucket."""
    client = get_s3_client()

    try:
        response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if "Contents" not in response:
            logger.info("No backups found in s3://%s/%s", bucket, prefix)
            return

        print(f"\n{'─'*65}")
        print(f"{'Key':<45} {'Size':>8}  {'Last Modified'}")
        print(f"{'─'*65}")

        for obj in response["Contents"]:
            size_kb = obj["Size"] / 1024
            modified = obj["LastModified"].strftime("%Y-%m-%d %H:%M")
            print(f"{obj['Key']:<45} {size_kb:>7.1f}KB  {modified}")

        print(f"{'─'*65}")
        print(f"Total objects: {len(response['Contents'])}\n")

    except Exception as e:
        logger.error("Failed to list backups: %s", e)


def main():
    print("\n=== S3 Backup Manager ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    bucket = input("Enter S3 bucket name: ").strip()
    if not bucket:
        print("Bucket name required.")
        return

    print("\n1. Upload single file")
    print("2. Upload directory")
    print("3. List backups")
    print("4. Exit")

    choice = input("\nSelect option: ").strip()

    if choice == "1":
        path = input("Enter file path: ").strip()
        upload_file(path, bucket)

    elif choice == "2":
        directory = input("Enter directory path: ").strip()
        prefix = input("S3 prefix (default: backups): ").strip() or "backups"
        upload_directory(directory, bucket, prefix)

    elif choice == "3":
        prefix = input("S3 prefix (default: backups): ").strip() or "backups"
        list_backups(bucket, prefix)

    elif choice == "4":
        print("Exiting.")

    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()
