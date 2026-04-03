"""
EC2 EBS Snapshot Manager
Author: Mustafa Talha Tuzsuz
GitHub: github.com/MustafaTuzsuz
Description: Automate EBS volume snapshots with retention policy.
             Tags snapshots for easy identification and cleanup.
"""

import boto3
import logging
from datetime import datetime, timezone, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def get_ec2_client(region: str = "eu-west-1"):
    return boto3.client("ec2", region_name=region)


def create_snapshot(volume_id: str, description: str = "", region: str = "eu-west-1"):
    """Create a snapshot of a given EBS volume."""
    client = get_ec2_client(region)

    if not description:
        description = f"auto-snapshot-{volume_id}-{datetime.now().strftime('%Y%m%d-%H%M')}"

    try:
        response = client.create_snapshot(
            VolumeId=volume_id,
            Description=description,
            TagSpecifications=[{
                "ResourceType": "snapshot",
                "Tags": [
                    {"Key": "Name", "Value": description},
                    {"Key": "CreatedBy", "Value": "ec2_snapshot.py"},
                    {"Key": "CreatedAt", "Value": datetime.now().strftime("%Y-%m-%d %H:%M")}
                ]
            }]
        )
        snapshot_id = response["SnapshotId"]
        logger.info("Snapshot created: %s for volume: %s", snapshot_id, volume_id)
        return snapshot_id

    except Exception as e:
        logger.error("Failed to create snapshot for volume %s: %s", volume_id, e)
        return None


def list_snapshots(owner_id: str = "self", region: str = "eu-west-1"):
    """List all snapshots owned by this account."""
    client = get_ec2_client(region)

    try:
        response = client.describe_snapshots(OwnerIds=[owner_id])
        snapshots = response["Snapshots"]

        if not snapshots:
            logger.info("No snapshots found.")
            return []

        print(f"\n{'─'*75}")
        print(f"{'SnapshotId':<25} {'VolumeId':<25} {'State':<12} {'StartTime'}")
        print(f"{'─'*75}")
        for s in snapshots:
            print(
                f"{s['SnapshotId']:<25} "
                f"{s.get('VolumeId','N/A'):<25} "
                f"{s['State']:<12} "
                f"{s['StartTime'].strftime('%Y-%m-%d %H:%M')}"
            )
        print(f"{'─'*75}\n")

        return snapshots

    except Exception as e:
        logger.error("Failed to list snapshots: %s", e)
        return []


def delete_old_snapshots(retention_days: int = 7, region: str = "eu-west-1"):
    """Delete snapshots older than retention_days. Dry-run logs before deletion."""
    client = get_ec2_client(region)
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

    try:
        response = client.describe_snapshots(
            OwnerIds=["self"],
            Filters=[{"Name": "tag:CreatedBy", "Values": ["ec2_snapshot.py"]}]
        )
        snapshots = response["Snapshots"]
        deleted = 0

        for s in snapshots:
            if s["StartTime"] < cutoff:
                logger.info(
                    "Deleting snapshot %s — created %s (older than %d days)",
                    s["SnapshotId"],
                    s["StartTime"].strftime("%Y-%m-%d"),
                    retention_days
                )
                client.delete_snapshot(SnapshotId=s["SnapshotId"])
                deleted += 1

        logger.info("Deleted %d snapshot(s) older than %d days.", deleted, retention_days)

    except Exception as e:
        logger.error("Failed to delete old snapshots: %s", e)


def main():
    print("\n=== EC2 Snapshot Manager ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    region = input("Enter AWS region (default: eu-west-1): ").strip() or "eu-west-1"

    print("\n1. Create snapshot")
    print("2. List snapshots")
    print("3. Delete snapshots older than N days")
    print("4. Exit")

    choice = input("\nSelect option: ").strip()

    if choice == "1":
        volume_id = input("Enter Volume ID (vol-xxxxxxxx): ").strip()
        if volume_id:
            create_snapshot(volume_id, region=region)

    elif choice == "2":
        list_snapshots(region=region)

    elif choice == "3":
        days = input("Delete snapshots older than (days, default 7): ").strip()
        retention = int(days) if days.isdigit() else 7
        delete_old_snapshots(retention_days=retention, region=region)

    elif choice == "4":
        print("Exiting.")

    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()
