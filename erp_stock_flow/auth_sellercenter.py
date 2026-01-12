import requests
from typing import Dict


def sellercenter_sign_in_get_token(login_url: str, username: str, password: str, timeout_seconds: int = 10) -> str:
    headers: Dict[str, str] = {"accept": "application/json"}
    body = {"username": username, "password": password}

    response = requests.post(login_url, json=body, headers=headers, timeout=timeout_seconds)
    if not response.ok:
        print("SC LOGIN STATUS:", response.status_code)
        print("SC LOGIN TEXT:", response.text[:1200])
        response.raise_for_status()

    payload = response.json()
    return payload["result"]["token"]