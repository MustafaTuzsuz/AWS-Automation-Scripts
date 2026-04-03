"""
IAM Audit Tool
Author: Mustafa Talha Tuzsuz
GitHub: github.com/MustafaTuzsuz
Description: Audit AWS IAM users, MFA status, and attached policies.
             Identifies security misconfigurations and access risks.
"""

import boto3
import logging
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def get_iam_client():
    return boto3.client("iam")


def list_users():
    """List all IAM users with creation date and last activity."""
    client = get_iam_client()

    try:
        response = client.list_users()
        users = response["Users"]

        if not users:
            logger.info("No IAM users found.")
            return []

        print(f"\n{'─'*75}")
        print(f"{'Username':<25} {'Created':<15} {'Last Used':<20} {'Password?'}")
        print(f"{'─'*75}")

        for user in users:
            username = user["UserName"]
            created = user["CreateDate"].strftime("%Y-%m-%d")

            # Last activity
            try:
                login_profile = client.get_login_profile(UserName=username)
                has_password = "Yes"
            except client.exceptions.NoSuchEntityException:
                has_password = "No"

            last_used = "Never"
            if "PasswordLastUsed" in user:
                last_used = user["PasswordLastUsed"].strftime("%Y-%m-%d %H:%M")

            print(f"{username:<25} {created:<15} {last_used:<20} {has_password}")

        print(f"{'─'*75}")
        print(f"Total users: {len(users)}\n")
        return users

    except Exception as e:
        logger.error("Failed to list users: %s", e)
        return []


def check_mfa_status():
    """Check MFA status for all IAM users — flag users without MFA."""
    client = get_iam_client()

    try:
        response = client.list_users()
        users = response["Users"]

        print(f"\n{'─'*55}")
        print(f"{'Username':<25} {'MFA Status':<15} {'Risk'}")
        print(f"{'─'*55}")

        no_mfa_users = []

        for user in users:
            username = user["UserName"]
            mfa_response = client.list_mfa_devices(UserName=username)
            mfa_devices = mfa_response["MFADevices"]

            if mfa_devices:
                status = "✅ Enabled"
                risk = "Low"
            else:
                status = "❌ Disabled"
                risk = "🚨 HIGH"
                no_mfa_users.append(username)

            print(f"{username:<25} {status:<15} {risk}")

        print(f"{'─'*55}")

        if no_mfa_users:
            print(f"\n⚠️  Users WITHOUT MFA ({len(no_mfa_users)}):")
            for u in no_mfa_users:
                print(f"   - {u}")
        else:
            print("\n✅ All users have MFA enabled.")

        print()

    except Exception as e:
        logger.error("Failed to check MFA status: %s", e)


def list_user_policies(username: str):
    """List all policies attached to a specific IAM user."""
    client = get_iam_client()

    try:
        # Managed policies
        managed = client.list_attached_user_policies(UserName=username)
        managed_policies = managed["AttachedPolicies"]

        # Inline policies
        inline = client.list_user_policies(UserName=username)
        inline_policies = inline["PolicyNames"]

        print(f"\n{'─'*55}")
        print(f"Policies for user: {username}")
        print(f"{'─'*55}")

        if managed_policies:
            print("\nManaged Policies:")
            for p in managed_policies:
                print(f"  - {p['PolicyName']} ({p['PolicyArn']})")
        else:
            print("\nManaged Policies: None")

        if inline_policies:
            print("\nInline Policies:")
            for p in inline_policies:
                print(f"  - {p}")
        else:
            print("Inline Policies: None")

        print()

    except Exception as e:
        logger.error("Failed to list policies for %s: %s", username, e)


def security_summary():
    """Run full IAM security audit and print summary report."""
    print("\n" + "="*55)
    print("       IAM SECURITY AUDIT REPORT")
    print(f"       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*55)

    print("\n[1] USER INVENTORY")
    users = list_users()

    print("[2] MFA STATUS CHECK")
    check_mfa_status()

    print("[3] POLICY AUDIT")
    for user in users:
        list_user_policies(user["UserName"])

    print("="*55)
    print("Audit complete.")
    print("="*55 + "\n")


def main():
    print("\n=== IAM Audit Tool ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("1. List all IAM users")
    print("2. Check MFA status")
    print("3. List policies for a user")
    print("4. Full security audit report")
    print("5. Exit")

    choice = input("\nSelect option: ").strip()

    if choice == "1":
        list_users()

    elif choice == "2":
        check_mfa_status()

    elif choice == "3":
        username = input("Enter IAM username: ").strip()
        if username:
            list_user_policies(username)

    elif choice == "4":
        security_summary()

    elif choice == "5":
        print("Exiting.")

    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()
