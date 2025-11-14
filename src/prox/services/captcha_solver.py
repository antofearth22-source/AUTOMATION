# This module contains the logic to interact with the TrueCaptcha API.

import logging
import base64
import requests
from typing import Optional

class TrueCaptchaService:
    """
    A service to solve CAPTCHAs using the TrueCaptcha API.
    """
    API_URL = "https://api.apitruecaptcha.org/one/gettext"

    def __init__(self, api_key: str, user_id: str, logger: logging.Logger):
        self.api_key = api_key
        self.user_id = user_id
        self.logger = logger

    def _encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """Reads an image file and encodes it into a base64 string."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            self.logger.error(f"CAPTCHA image file not found at path: {image_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error encoding image to base64: {e}")
            return None

    def solve_from_image_path(self, image_path: str) -> Optional[str]:
        """
        Solves a CAPTCHA from an image file by sending it to the TrueCaptcha API.

        Args:
            image_path: The local file path to the CAPTCHA image.

        Returns:
            The solved CAPTCHA text, or None if solving fails.
        """
        self.logger.info("Attempting to solve CAPTCHA with TrueCaptcha service.")

        if not self.api_key or not self.user_id:
            self.logger.warning("TrueCaptcha API key or User ID is not configured. Skipping.")
            return None

        base64_image = self._encode_image_to_base64(image_path)
        if not base64_image:
            return None

        payload = {
            "userid": self.user_id,
            "apikey": self.api_key,
            "data": base64_image,
            "mode": "auto"
        }

        try:
            response = requests.post(self.API_URL, json=payload, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            response_data = response.json()

            if "result" in response_data:
                solved_text = response_data["result"]
                self.logger.info(f"TrueCaptcha solved the CAPTCHA: '{solved_text}'")
                return solved_text
            else:
                self.logger.error(f"TrueCaptcha API did not return a result. Response: {response_data}")
                return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred while calling TrueCaptcha API: {e}")
            return None
        except ValueError:
            self.logger.error(f"Failed to decode JSON response from TrueCaptcha API. Response text: {response.text}")
            return None
