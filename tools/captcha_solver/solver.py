import os
import base64
import time
import requests
from typing import Dict, Any

# Constants from TrueCaptcha documentation
API_URL = "https://api.truecaptcha.org/in.php"
RESULT_URL = "https://api.truecaptcha.org/res.php"

def solve_captcha(image_path: str, timeout: int) -> Dict[str, Any]:
    """
    Solves a CAPTCHA using the TrueCaptcha service, with retries and polling.

    Args:
        image_path: The local path to the CAPTCHA image file.
        timeout: The total time in seconds to wait for a solution.

    Returns:
        A dictionary containing the result of the operation.
    """
    start_time = time.monotonic()

    user_id = os.getenv("TRUECAPTCHA_USERID")
    api_key = os.getenv("TRUECAPTCHA_APIKEY")

    if not user_id or not api_key:
        return {"ok": False, "error": "Missing TRUECAPTCHA_USERID or TRUECAPTCHA_APIKEY.", "provider": "truecaptcha"}

    try:
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        return {"ok": False, "error": f"Image file not found at: {image_path}", "provider": "truecaptcha"}
    except Exception as e:
        return {"ok": False, "error": f"Failed to read or encode image: {e}", "provider": "truecaptcha"}

    # --- Initial request to submit the CAPTCHA ---
    payload = {
        'key': api_key,
        'method': 'post',
        'body': image_base64,
        'json': 1,
        'userid': user_id,
    }

    try:
        response = requests.post(API_URL, data=payload, timeout=10) # 10s timeout for initial submission
        response.raise_for_status()
        result = response.json()

        if result.get('status') != 1:
            return {"ok": False, "error": f"API Error: {result.get('request', 'Unknown error')}", "provider": "truecaptcha"}

        captcha_id = result['request']

    except requests.exceptions.RequestException as e:
        return {"ok": False, "error": f"Network error during submission: {e}", "provider": "truecaptcha"}

    # --- Polling for the result ---
    time.sleep(5) # Initial wait as per docs
    while time.monotonic() - start_time < timeout:
        try:
            params = {
                'key': api_key,
                'action': 'get',
                'id': captcha_id,
                'json': 1,
            }
            res_response = requests.get(RESULT_URL, params=params, timeout=5) # 5s timeout for polling
            res_response.raise_for_status()
            result = res_response.json()

            if result.get('status') == 1:
                return {
                    "ok": True,
                    "text": result.get('request', ''),
                    "confidence": 0.9, # TrueCaptcha does not provide confidence
                    "provider": "truecaptcha"
                }
            elif result.get('request') == 'CAPCHA_NOT_READY':
                time.sleep(2) # Wait and poll again
                continue
            else:
                return {"ok": False, "error": f"API Error on result poll: {result.get('request')}", "provider": "truecaptcha"}

        except requests.exceptions.RequestException:
            # Continue polling on network error, but respect timeout
            time.sleep(2)
            continue

    return {"ok": False, "error": "Timeout exceeded while waiting for CAPTCHA solution.", "provider": "truecaptcha"}
