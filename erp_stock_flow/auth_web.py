import requests
from typing import Dict


def web_sign_in_get_bearer_token(login_url: str, user_email: str, user_password: str, timeout_seconds: int = 30) -> str:
    headers: Dict[str, str] = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "es-ES,es;q=0.9",
        "content-type": "application/json",
        "origin": "https://quality.farmatouch.com",
        "referer": "https://quality.farmatouch.com/",
        "user-agent": "Mozilla/5.0",
    }

    body = {"email": user_email, "password": user_password}

    response = requests.post(login_url, headers=headers, json=body, timeout=timeout_seconds)
    if not response.ok:
        print("WEB LOGIN STATUS:", response.status_code)
        print("WEB LOGIN TEXT:", response.text[:1200])
        response.raise_for_status()

    return response.json()["token"]