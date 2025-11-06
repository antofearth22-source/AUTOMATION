import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.automation.captcha_gateway import CaptchaGateway

class TestCaptchaGateway(unittest.TestCase):

    def setUp(self):
        # Create a dummy solver file for initialization
        self.dummy_solver_path = Path(__file__).parent / "dummy_solver.exe"
        with open(self.dummy_solver_path, "w") as f:
            f.write("#!/bin/bash\necho '{\"ok\": true}'")

        # Create a dummy image file
        self.dummy_image_path = Path(__file__).parent / "dummy_image.png"
        self.dummy_image_path.touch()

    def tearDown(self):
        # Clean up dummy files
        if self.dummy_solver_path.exists():
            self.dummy_solver_path.unlink()
        if self.dummy_image_path.exists():
            self.dummy_image_path.unlink()

    def test_init_raises_error_if_solver_not_found(self):
        """Test that FileNotFoundError is raised if the solver executable does not exist."""
        with self.assertRaises(FileNotFoundError):
            CaptchaGateway("non_existent_solver.exe")

    @patch('subprocess.run')
    def test_solve_success(self, mock_subprocess_run):
        """Test the successful path where the solver returns valid JSON."""
        # Mock the subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"ok": True, "text": "abcde"})
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        gateway = CaptchaGateway(str(self.dummy_solver_path))
        result = gateway.solve(str(self.dummy_image_path))

        self.assertTrue(result["ok"])
        self.assertEqual(result["text"], "abcde")
        mock_subprocess_run.assert_called_once()

    @patch('subprocess.run')
    def test_solve_handles_solver_process_error(self, mock_subprocess_run):
        """Test handling of a non-zero exit code from the solver."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Something went wrong"
        mock_subprocess_run.return_value = mock_result

        gateway = CaptchaGateway(str(self.dummy_solver_path))
        result = gateway.solve(str(self.dummy_image_path))

        self.assertFalse(result["ok"])
        self.assertIn("Solver process failed", result["error"])

    @patch('subprocess.run')
    def test_solve_handles_invalid_json(self, mock_subprocess_run):
        """Test handling of non-JSON output from the solver."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "This is not JSON"
        mock_subprocess_run.return_value = mock_result

        gateway = CaptchaGateway(str(self.dummy_solver_path))
        result = gateway.solve(str(self.dummy_image_path))

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "Invalid JSON response from solver.")

    @patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="dummy", timeout=10))
    def test_solve_handles_timeout(self, mock_subprocess_run):
        """Test handling of a subprocess timeout."""
        gateway = CaptchaGateway(str(self.dummy_solver_path))
        result = gateway.solve(str(self.dummy_image_path))

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "Solver process timed out.")

if __name__ == '__main__':
    unittest.main()
