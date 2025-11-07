import unittest
from unittest.mock import patch
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.security.credential_store import CredentialStore

class TestCredentialStore(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(__file__).parent / 'temp_vault_data'
        self.test_dir.mkdir(exist_ok=True)
        self.mock_appdata = patch.dict(os.environ, {'APPDATA': str(self.test_dir)})
        self.mock_appdata.start()
        self.store = CredentialStore()

    def tearDown(self):
        self.mock_appdata.stop()
        config_dir = self.test_dir / "IrctcPro" / "config"
        if config_dir.exists():
            for f in config_dir.iterdir():
                f.unlink()
            config_dir.rmdir()
            (self.test_dir / "IrctcPro").rmdir()
        if self.test_dir.exists():
            self.test_dir.rmdir()

    def test_initialization_creates_files(self):
        self.assertTrue(self.store.config_dir.exists())
        self.assertTrue(self.store.index_path.exists())
        index = self.store._read_index()
        self.assertEqual(index, {"version": 1, "default_slot": None, "slots": []})

    @patch('keyring.set_password')
    def test_create_and_list_slots(self, mock_set_password):
        slot_id = self.store.create_slot("Personal", "testuser1", "pass123")
        self.assertIsNotNone(slot_id)

        slots = self.store.list_slots()
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0]['label'], "Personal")

        mock_set_password.assert_called_with(CredentialStore.SERVICE_NAME, f"{slot_id}/password", "pass123")

    @patch('keyring.get_password')
    @patch('keyring.set_password')
    def test_get_credentials(self, mock_set_password, mock_get_password):
        def get_password_mock(service, username):
            if "password" in username:
                return "retrieved_pass"
            if "totp" in username:
                return "retrieved_totp"
            return None
        mock_get_password.side_effect = get_password_mock

        slot_id = self.store.create_slot("Work", "workuser", "workpass", totp_secret="worktotp")
        creds = self.store.get_credentials(slot_id)

        self.assertEqual(creds['userid'], "workuser")
        self.assertEqual(creds['password'], "retrieved_pass")
        self.assertEqual(creds['totp_secret'], "retrieved_totp")

    @patch('keyring.delete_password')
    @patch('keyring.set_password')
    def test_delete_slot(self, mock_set_password, mock_delete_password):
        slot_id = self.store.create_slot("Temp", "tempuser", "temppass")
        self.assertEqual(len(self.store.list_slots()), 1)

        self.store.delete_slot(slot_id)

        self.assertEqual(len(self.store.list_slots()), 0)
        mock_delete_password.assert_any_call(CredentialStore.SERVICE_NAME, f"{slot_id}/password")

    @patch('keyring.set_password')
    def test_update_slot(self, mock_set_password):
        slot_id = self.store.create_slot("Initial", "user", "pass1")
        mock_set_password.reset_mock() # Reset after creation call

        self.store.update_slot(slot_id, label="Updated Label", password="new_password")

        slots = self.store.list_slots()
        self.assertEqual(slots[0]['label'], "Updated Label")

        mock_set_password.assert_called_with(CredentialStore.SERVICE_NAME, f"{slot_id}/password", "new_password")

    @patch('keyring.set_password')
    def test_set_and_get_default_slot(self, mock_set_password):
        self.store.create_slot("Slot 1", "user1", "pass1")
        slot_id_2 = self.store.create_slot("Slot 2", "user2", "pass2")

        self.assertIsNone(self.store.get_default_slot())
        self.store.set_default_slot(slot_id_2)

        default_slot = self.store.get_default_slot()
        self.assertIsNotNone(default_slot)
        self.assertEqual(default_slot['slot_id'], slot_id_2)

if __name__ == '__main__':
    unittest.main()
