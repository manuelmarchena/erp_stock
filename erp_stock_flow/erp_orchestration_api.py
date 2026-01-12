import requests
from typing import Any, Dict, List


def request_stock(
    request_stock_url: str,
    web_bearer_token: str,
    order_id: str,
    pharmacies: List[Dict[str, Any]],
    timeout_seconds: int = 30,
) -> str:
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {web_bearer_token}",
    }

    body = {
        "orderId": order_id,
        "pharmacies": pharmacies,
    }

    response = requests.post(request_stock_url, headers=headers, json=body, timeout=timeout_seconds)
    if not response.ok:
        print("REQUEST_STOCK STATUS:", response.status_code)
        print("REQUEST_STOCK TEXT:", response.text[:1200])
        response.raise_for_status()

    payload = response.json()

    # Tu caso anterior: payload["data"]["traceId"]
    trace_id = None
    if isinstance(payload.get("data"), dict):
        trace_id = payload["data"].get("traceId") or payload["data"].get("TraceId")
    trace_id = trace_id or payload.get("traceId") or payload.get("TraceId")

    if not trace_id:
        raise KeyError(f"No pude encontrar traceId en response: {payload}")

    return str(trace_id)