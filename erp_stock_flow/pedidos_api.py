import requests
from typing import Any, Dict, Optional

def get_customer_default_address_by_customer_id(
    url: str,
    web_bearer_token: str,
    customer_id: str,
    farma_access_token: Optional[str] = None,
    cookies_header_value: Optional[str] = None,
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    params = {"CustomerId": customer_id}

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {web_bearer_token}",
    }

    # opcionales (por si tu ambiente los requiere)
    if farma_access_token:
        headers["farma-access-token"] = farma_access_token
    if cookies_header_value:
        headers["cookie"] = cookies_header_value

    resp = requests.get(url, params=params, headers=headers, timeout=timeout_seconds)

    if not resp.ok:
        print("DEFAULT-ADDRESS URL:", resp.url)
        print("DEFAULT-ADDRESS STATUS:", resp.status_code)
        print("DEFAULT-ADDRESS TEXT:", resp.text[:1200])

    resp.raise_for_status()
    return resp.json()

def get_stock_request_data(
    base_url: str,
    web_bearer_token: str,
    order_id: str,
    suffix: str = "stock-request-data",
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    """
    Pedidos Core -> GET /api/v1/order/{orderId}/stock-request-data

    base_url debe ser algo como:
      https://quality.farmatouch.com/pedidos-core-backend/api/v1/order
    """
    url = f"{base_url}/{order_id}/{suffix}"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {web_bearer_token}",
    }

    resp = requests.get(url, headers=headers, timeout=timeout_seconds)

    if not resp.ok:
        print("STOCK-REQUEST-DATA URL:", resp.url)
        print("STOCK-REQUEST-DATA STATUS:", resp.status_code)
        print("STOCK-REQUEST-DATA TEXT:", resp.text[:1200])

    resp.raise_for_status()
    return resp.json()


def get_order_by_id(
    base_url: str,
    web_bearer_token: str,
    order_id: str,
    farma_access_token: Optional[str] = None,
    cookies_header_value: Optional[str] = None,
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    """
    (Se deja por compatibilidad / debug)
    GetOrder?id=...
    """
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "es-ES,es;q=0.9",
        "authorization": f"Bearer {web_bearer_token}",
        "referer": "https://quality.farmatouch.com/",
        "origin": "https://quality.farmatouch.com",
        "user-agent": "Mozilla/5.0",
    }

    if farma_access_token:
        headers["farma-access-token"] = farma_access_token

    if cookies_header_value:
        headers["cookie"] = cookies_header_value

    resp = requests.get(
        base_url,
        params={"id": order_id},
        headers=headers,
        timeout=timeout_seconds,
    )

    if not resp.ok:
        print("GETORDER URL:", resp.url)
        print("GETORDER STATUS:", resp.status_code)
        print("GETORDER TEXT:", resp.text[:1200])

    resp.raise_for_status()
    return resp.json()