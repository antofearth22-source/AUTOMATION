import argparse
import sys
import os

# Add project root to path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.security.credential_store import CredentialStore

def main():
    """CLI for managing the credential vault."""
    parser = argparse.ArgumentParser(description="IRCTC Pro Vault Management Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- List command ---
    subparsers.add_parser("list", help="List all account slots.")

    # --- Set-default command ---
    setdefault_parser = subparsers.add_parser("set-default", help="Set a slot as the default.")
    setdefault_parser.add_argument("slot_id", help="The ID of the slot to set as default.")

    # --- Delete command ---
    delete_parser = subparsers.add_parser("delete", help="Delete an account slot.")
    delete_parser.add_argument("slot_id", help="The ID of the slot to delete.")

    args = parser.parse_args()

    try:
        store = CredentialStore()

        if args.command == "list":
            slots = store.list_slots()
            default_slot = store.get_default_slot()
            if not slots:
                print("No account slots found.")
                return

            print(f"{'DEFAULT':<10} {'SLOT ID':<40} {'LABEL':<20} {'IRCTC USER ID'}")
            print("-" * 100)
            for slot in slots:
                is_default = "Yes" if default_slot and default_slot["slot_id"] == slot["slot_id"] else ""
                print(f"{is_default:<10} {slot['slot_id']:<40} {slot['label']:<20} {slot['irctc_userid']}")

        elif args.command == "set-default":
            store.set_default_slot(args.slot_id)
            print(f"Successfully set '{args.slot_id}' as the default slot.")

        elif args.command == "delete":
            confirm = input(f"Are you sure you want to delete slot '{args.slot_id}'? This cannot be undone. [y/N]: ")
            if confirm.lower() == 'y':
                store.delete_slot(args.slot_id)
                print(f"Successfully deleted slot '{args.slot_id}'.")
            else:
                print("Deletion cancelled.")

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
