"""
EC2 Instance Manager
Author: Mustafa Talha Tuzsuz
GitHub: github.com/MustafaTuzsuz
Description: Start, stop, and list AWS EC2 instances using boto3.
             Follows least-privilege IAM principles.
             Credentials loaded from environment variables only.
"""

import boto3
import logging
from datetime import datetime

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def get_ec2_client(region: str = "eu-west-1"):
    """Create and return an EC2 client for the given region."""
    return boto3.client("ec2", region_name=region)


def list_instances(region: str = "eu-west-1"):
    """List all EC2 instances with their current state."""
    client = get_ec2_client(region)
    
    try:
        response = client.describe_instances()
        instances = []

        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                name = "N/A"
                if "Tags" in instance:
                    for tag in instance["Tags"]:
                        if tag["Key"] == "Name":
                            name = tag["Value"]

                instances.append({
                    "InstanceId": instance["InstanceId"],
                    "Name": name,
                    "State": instance["State"]["Name"],
                    "Type": instance["InstanceType"],
                    "LaunchTime": instance["LaunchTime"].strftime("%Y-%m-%d %H:%M")
                })

        if not instances:
            logger.info("No instances found in region: %s", region)
            return []

        print(f"\n{'─'*65}")
        print(f"{'ID':<22} {'Name':<20} {'State':<12} {'Type':<12} {'Launched'}")
        print(f"{'─'*65}")
        for i in instances:
            print(f"{i['InstanceId']:<22} {i['Name']:<20} {i['State']:<12} {i['Type']:<12} {i['LaunchTime']}")
        print(f"{'─'*65}\n")

        return instances

    except Exception as e:
        logger.error("Failed to list instances: %s", e)
        return []


def start_instance(instance_id: str, region: str = "eu-west-1"):
    """Start a stopped EC2 instance by ID."""
    client = get_ec2_client(region)

    try:
        response = client.start_instances(InstanceIds=[instance_id])
        state = response["StartingInstances"][0]["CurrentState"]["Name"]
        logger.info("Instance %s state: %s", instance_id, state)
        return state

    except Exception as e:
        logger.error("Failed to start instance %s: %s", instance_id, e)
        return None


def stop_instance(instance_id: str, region: str = "eu-west-1"):
    """Stop a running EC2 instance by ID."""
    client = get_ec2_client(region)

    try:
        response = client.stop_instances(InstanceIds=[instance_id])
        state = response["StoppingInstances"][0]["CurrentState"]["Name"]
        logger.info("Instance %s state: %s", instance_id, state)
        return state

    except Exception as e:
        logger.error("Failed to stop instance %s: %s", instance_id, e)
        return None


def main():
    print("\n=== EC2 Instance Manager ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    region = input("Enter AWS region (default: eu-west-1): ").strip() or "eu-west-1"

    print("\n1. List instances")
    print("2. Start instance")
    print("3. Stop instance")
    print("4. Exit")

    choice = input("\nSelect option: ").strip()

    if choice == "1":
        list_instances(region)

    elif choice == "2":
        list_instances(region)
        instance_id = input("Enter Instance ID to start: ").strip()
        if instance_id:
            start_instance(instance_id, region)

    elif choice == "3":
        list_instances(region)
        instance_id = input("Enter Instance ID to stop: ").strip()
        if instance_id:
            stop_instance(instance_id, region)

    elif choice == "4":
        print("Exiting.")

    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()
