import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

import keyring
import keyring.errors

class CredentialStore:
    """
    Manages secure storage of IRCTC account credentials ("slots").

    - Metadata is stored in a JSON file in the user's AppData.
    - Secrets (passwords, TOTP) are stored securely in the Windows Credential Manager.
    """
    SERVICE_NAME = "IrctcPro"

    def __init__(self):
        app_data_path = os.getenv("APPDATA")
        if not app_data_path:
            raise RuntimeError("APPDATA environment variable is not set.")

        self.config_dir = Path(app_data_path) / "IrctcPro" / "config"
        self.index_path = self.config_dir / "vault_index.json"
        self._ensure_store_initialized()

    def _ensure_store_initialized(self):
        """Creates the config directory and index file if they don't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_path.is_file():
            self._write_index({"version": 1, "default_slot": None, "slots": []})
        else:
            # Handle potential corruption
            try:
                self._read_index()
            except (json.JSONDecodeError, KeyError):
                backup_path = self.index_path.with_suffix(".json.bak")
                self.index_path.rename(backup_path)
                self._write_index({"version": 1, "default_slot": None, "slots": []})

    def _read_index(self) -> Dict[str, Any]:
        with open(self.index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "version" not in data or "slots" not in data:
                raise KeyError("Index file is missing required keys.")
            return data

    def _write_index(self, data: Dict[str, Any]):
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _now_utc(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def mask(value: Optional[str]) -> str:
        if not value or len(value) < 6:
            return "******"
        return f"{value[:3]}***{value[-2:]}"

    def create_slot(self, label: str, irctc_userid: str, password: str, totp_secret: Optional[str] = None) -> str:
        """Creates a new slot and stores its credentials securely."""
        index = self._read_index()
        slot_id = f"slot_{uuid.uuid4().hex}"
        now = self._now_utc()

        new_slot = {
            "slot_id": slot_id,
            "label": label,
            "irctc_userid": irctc_userid,
            "created_utc": now,
            "updated_utc": now,
            "notes": ""
        }
        index["slots"].append(new_slot)

        # Store secrets in Credential Manager
        keyring.set_password(self.SERVICE_NAME, f"{slot_id}/password", password)
        if totp_secret:
            keyring.set_password(self.SERVICE_NAME, f"{slot_id}/totp", totp_secret)

        self._write_index(index)
        return slot_id

    def list_slots(self) -> List[Dict[str, Any]]:
        """Returns a list of all slot metadata (no secrets)."""
        return self._read_index().get("slots", [])

    def get_credentials(self, slot_id: str) -> Dict[str, Optional[str]]:
        """Retrieves the credentials for a given slot_id."""
        slots = {s["slot_id"]: s for s in self.list_slots()}
        if slot_id not in slots:
            raise ValueError(f"Slot with ID '{slot_id}' not found.")

        try:
            password = keyring.get_password(self.SERVICE_NAME, f"{slot_id}/password")
            totp_secret = keyring.get_password(self.SERVICE_NAME, f"{slot_id}/totp")
        except keyring.errors.NoKeyringError:
            raise RuntimeError("Windows Credential Manager is not available.")

        return {
            "userid": slots[slot_id]["irctc_userid"],
            "password": password,
            "totp_secret": totp_secret
        }

    def delete_slot(self, slot_id: str):
        """Deletes a slot and its associated credentials."""
        index = self._read_index()

        # Remove from index
        original_count = len(index["slots"])
        index["slots"] = [s for s in index["slots"] if s["slot_id"] != slot_id]
        if len(index["slots"]) == original_count:
            raise ValueError(f"Slot with ID '{slot_id}' not found.")

        if index.get("default_slot") == slot_id:
            index["default_slot"] = None

        # Delete secrets from Credential Manager
        try:
            keyring.delete_password(self.SERVICE_NAME, f"{slot_id}/password")
            # It's okay if totp secret doesn't exist
            keyring.delete_password(self.SERVICE_NAME, f"{slot_id}/totp")
        except keyring.errors.PasswordDeleteError:
            # This can happen if the secret doesn't exist, which is fine.
            pass

        self._write_index(index)

    def update_slot(self, slot_id: str, label: Optional[str] = None, irctc_userid: Optional[str] = None,
                    password: Optional[str] = None, totp_secret: Optional[str] = None, notes: Optional[str] = None):
        """Updates metadata and credentials for an existing slot."""
        index = self._read_index()
        slot_found = False
        for slot in index["slots"]:
            if slot["slot_id"] == slot_id:
                if label is not None:
                    slot["label"] = label
                if irctc_userid is not None:
                    slot["irctc_userid"] = irctc_userid
                if notes is not None:
                    slot["notes"] = notes
                slot["updated_utc"] = self._now_utc()
                slot_found = True
                break

        if not slot_found:
            raise ValueError(f"Slot with ID '{slot_id}' not found.")

        # Update secrets if provided
        if password is not None:
            keyring.set_password(self.SERVICE_NAME, f"{slot_id}/password", password)
        if totp_secret is not None:
            keyring.set_password(self.SERVICE_NAME, f"{slot_id}/totp", totp_secret)

        self._write_index(index)

    def set_default_slot(self, slot_id: Optional[str]):
        """Sets the given slot_id as the default."""
        index = self._read_index()

        if slot_id and not any(s["slot_id"] == slot_id for s in index["slots"]):
            raise ValueError(f"Slot with ID '{slot_id}' not found.")

        index["default_slot"] = slot_id
        self._write_index(index)

    def get_default_slot(self) -> Optional[Dict[str, Any]]:
        """Returns the metadata for the default slot, if one is set."""
        index = self._read_index()
        default_id = index.get("default_slot")
        if not default_id:
            return None

        return next((s for s in index["slots"] if s["slot_id"] == default_id), None)
