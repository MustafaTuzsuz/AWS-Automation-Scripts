"""
S3 Cleanup Manager
Author: Mustafa Talha Tuzsuz
GitHub: github.com/MustafaTuzsuz
Description: Delete old S3 objects based on retention policy.
             Includes dry-run mode — preview before deletion.
"""

import boto3
import logging
from datetime import datetime, timezone, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def get_s3_client():
    return boto3.client("s3")


def list_old_objects(bucket: str, prefix: str = "backups", retention_days: int = 30):
    """Return list of objects older than retention_days."""
    client = get_s3_client()
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    old_objects = []

    try:
        paginator = client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

        for page in pages:
            if "Contents" not in page:
                continue
            for obj in page["Contents"]:
                if obj["LastModified"] < cutoff:
                    old_objects.append(obj)

        return old_objects

    except Exception as e:
        logger.error("Failed to list objects: %s", e)
        return []


def dry_run(bucket: str, prefix: str = "backups", retention_days: int = 30):
    """Preview objects that would be deleted — no actual deletion."""
    old_objects = list_old_objects(bucket, prefix, retention_days)

    if not old_objects:
        print(f"\nNo objects older than {retention_days} days found.")
        return

    print(f"\n{'─'*65}")
    print(f"DRY RUN — Objects that WOULD be deleted (>{retention_days} days old):")
    print(f"{'─'*65}")
    print(f"{'Key':<45} {'Size':>8}  {'Last Modified'}")
    print(f"{'─'*65}")

    total_size = 0
    for obj in old_objects:
        size_kb = obj["Size"] / 1024
        total_size += obj["Size"]
        modified = obj["LastModified"].strftime("%Y-%m-%d %H:%M")
        print(f"{obj['Key']:<45} {size_kb:>7.1f}KB  {modified}")

    print(f"{'─'*65}")
    print(f"Total: {len(old_objects)} objects | {total_size/1024:.1f} KB would be freed")
    print(f"Run with --delete flag to execute deletion.\n")


def delete_old_objects(bucket: str, prefix: str = "backups", retention_days: int = 30):
    """Delete objects older than retention_days from S3 bucket."""
    old_objects = list_old_objects(bucket, prefix, retention_days)

    if not old_objects:
        logger.info("No objects older than %d days found.", retention_days)
        return

    client = get_s3_client()
    deleted = 0
    failed = 0

    print(f"\n{'─'*50}")
    print(f"Deleting {len(old_objects)} objects older than {retention_days} days...")
    print(f"{'─'*50}")

    # Batch delete — max 1000 per request
    batch = [{"Key": obj["Key"]} for obj in old_objects]

    try:
        response = client.delete_objects(
            Bucket=bucket,
            Delete={"Objects": batch, "Quiet": False}
        )

        deleted = len(response.get("Deleted", []))
        errors = response.get("Errors", [])
        failed = len(errors)

        for err in errors:
            logger.error("Failed to delete %s: %s", err["Key"], err["Message"])

    except Exception as e:
        logger.error("Batch delete failed: %s", e)

    print(f"\nCleanup complete — Deleted: {deleted} | Failed: {failed}")
    print(f"Bucket: s3://{bucket}/{prefix}/\n")


def main():
    print("\n=== S3 Cleanup Manager ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    bucket = input("Enter S3 bucket name: ").strip()
    if not bucket:
        print("Bucket name required.")
        return

    prefix = input("S3 prefix (default: backups): ").strip() or "backups"
    days = input("Retention period in days (default: 30): ").strip()
    retention_days = int(days) if days.isdigit() else 30

    print("\n1. Dry run — preview objects to delete")
    print("2. Delete old objects")
    print("3. Exit")

    choice = input("\nSelect option: ").strip()

    if choice == "1":
        dry_run(bucket, prefix, retention_days)

    elif choice == "2":
        confirm = input(
            f"\n⚠️  This will DELETE objects older than {retention_days} days "
            f"from s3://{bucket}/{prefix}/\nType 'yes' to confirm: "
        ).strip().lower()

        if confirm == "yes":
            delete_old_objects(bucket, prefix, retention_days)
        else:
            print("Cancelled.")

    elif choice == "3":
        print("Exiting.")

    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()
