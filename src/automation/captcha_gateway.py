import subprocess
import json
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class CaptchaGateway:
    """
    An adapter to an external CLI-based CAPTCHA solving executable.
    This class is responsible for invoking the process, handling timeouts,
    and parsing the JSON output.
    """
    def __init__(self, solver_path: str):
        self.solver_path = Path(solver_path)
        if not self.solver_path.is_file():
            raise FileNotFoundError(f"CAPTCHA solver executable not found at: {self.solver_path}")

    def solve(self, image_path: str, timeout: int = 25) -> Dict[str, Any]:
        """
        Calls the external solver to solve the CAPTCHA image.

        Args:
            image_path: The absolute path to the CAPTCHA image.
            timeout: The maximum time to wait for the solver to finish.

        Returns:
            A dictionary containing the parsed JSON response from the solver.
        """
        command = [
            str(self.solver_path),
            "--solve",
            image_path,
            "--timeout",
            str(timeout)
        ]

        try:
            logger.info("Invoking external CAPTCHA solver...")
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout + 5,  # Give a little buffer over the internal timeout
                check=False  # We check the return code manually
            )

            if process.returncode != 0:
                logger.error(f"Solver process failed with exit code {process.returncode}. Stderr: {process.stderr.strip()}")
                return {"ok": False, "error": "Solver process failed. See logs for details."}

            try:
                result = json.loads(process.stdout)
                logger.info(f"CAPTCHA solver returned a result. Success: {result.get('ok')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from solver output: {process.stdout}")
                return {"ok": False, "error": "Invalid JSON response from solver."}

        except subprocess.TimeoutExpired:
            logger.error("Timeout expired while waiting for the CAPTCHA solver process.")
            return {"ok": False, "error": "Solver process timed out."}
        except Exception as e:
            logger.exception(f"An unexpected error occurred while running the CAPTCHA solver: {e}")
            return {"ok": False, "error": "An unexpected error occurred with the solver."}
