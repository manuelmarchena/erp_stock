from typing import Any, Dict
import requests


def publish_stock_response(
    publish_url: str,
    web_bearer_token: str,
    trace_id: str,
    body: Dict[str, Any],
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {web_bearer_token}",
        "X-Correlation-Id": trace_id,
    }

    resp = requests.post(publish_url, headers=headers, json=body, timeout=timeout_seconds)

    raw = {
        "url": resp.url,
        "status_code": resp.status_code,
        "headers": dict(resp.headers),
        "text": resp.text,
    }

    # Si querés, agregamos también el json parseado (sin reemplazar lo crudo)
    try:
        raw["json"] = resp.json()
    except ValueError:
        raw["json"] = None

    # Si querés que el flujo corte al fallar:
    if not resp.ok:
        # igual ya devolvemos raw, pero levantamos error para que te enteres
        resp.raise_for_status()

    return raw