from typing import Any, Dict, List, Optional, Tuple
import math
import json
import time 
from .config import (
    WEB_LOGIN_URL,
    SELLERCENTER_LOGIN_URL,
    BY_LOCATION_APP_URL,
    REQUEST_STOCK_URL,
    PUBLISH_STOCK_RESPONSE_URL,
    STOCK_REQUEST_DATA_BASE_URL,
    STOCK_REQUEST_DATA_SUFFIX,
)

from .auth_web import web_sign_in_get_bearer_token
from .auth_sellercenter import sellercenter_sign_in_get_token
from .pedidos_api import get_stock_request_data
from .sellercenter_api import get_pharmacies_by_location_app
from .erp_orchestration_api import request_stock
from .erp_integration_api import publish_stock_response
from .mappers import (
    extract_order_number_and_items,
    build_publish_stock_response_body,
)


def _split_half_true_half_false(total: int) -> List[bool]:
    true_count = math.ceil(total / 2)
    false_count = total - true_count
    return ([True] * true_count) + ([False] * false_count)


def _make_partial_one_item_unavailable(items_count: int, unavailable_index: int = 0) -> List[bool]:
    """
    PARTIAL: todos True excepto 1 False.
    - Si hay 0 items: []
    - Si hay 1 item: no hay partial real -> [False]
    """
    if items_count <= 0:
        return []
    if items_count == 1:
        return [False]

    plan = [True] * items_count
    idx = max(0, min(unavailable_index, items_count - 1))
    plan[idx] = False
    return plan


def _pretty(obj: Any) -> str:
    """Pretty JSON para dict/list; fallback a str(obj)."""
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except TypeError:
        return str(obj)


def _get_tokens(
    web_email: str,
    web_password: str,
    sellercenter_username: str,
    sellercenter_password: str,
) -> Tuple[str, str]:
    web_bearer_token = web_sign_in_get_bearer_token(WEB_LOGIN_URL, web_email, web_password)

    sellercenter_token = sellercenter_sign_in_get_token(
        SELLERCENTER_LOGIN_URL, sellercenter_username, sellercenter_password
    )

    return web_bearer_token, sellercenter_token


def _get_pharmacies(
    sellercenter_token: str,
    customer_id: str,
    latitude: float,
    longitude: float,
    items_per_page: int,
) -> List[Dict[str, Any]]:
    pharmacies = get_pharmacies_by_location_app(
        BY_LOCATION_APP_URL,
        sellercenter_token=sellercenter_token,
        customer_id=customer_id,
        latitude=latitude,
        longitude=longitude,
        items_per_page=items_per_page,
    )
    return pharmacies


def _get_trace_id(
    web_bearer_token: str,
    order_id: str,
    pharmacies: List[Dict[str, Any]],
) -> str:
    trace_id = request_stock(
        REQUEST_STOCK_URL,
        web_bearer_token=web_bearer_token,
        order_id=order_id,
        pharmacies=pharmacies,
    )
    return trace_id


def _get_order_key_and_items(
    web_bearer_token: str,
    order_id: str,
) -> Tuple[str, List[Dict[str, Any]]]:
    stock_request_data_json = get_stock_request_data(
        base_url=STOCK_REQUEST_DATA_BASE_URL,
        order_id=order_id,
        suffix=STOCK_REQUEST_DATA_SUFFIX,
        web_bearer_token=web_bearer_token,
    )

    order_key, stock_items = extract_order_number_and_items(stock_request_data_json)
    return order_key, stock_items


def _pick_partial_pharmacy_index(pharmacies_plan: List[bool]) -> Optional[int]:
    """
    Elegimos 1 farmacia FULL para hacerla PARTIAL (la primera True).
    Si no hay ninguna True, no hay PARTIAL.
    """
    return next((i for i, is_full in enumerate(pharmacies_plan) if is_full), None)


def _status_for_pharmacy(idx: int, is_full: bool, partial_pharmacy_index: Optional[int]) -> str:
    if partial_pharmacy_index is not None and idx == partial_pharmacy_index:
        return "PARTIAL"
    return "FULL_STOCK" if is_full else "NO_STOCK"


def _build_publish_body_and_status(
    idx: int,
    pharmacy: Dict[str, Any],
    is_full: bool,
    partial_pharmacy_index: Optional[int],
    order_key: str,
    stock_items: List[Dict[str, Any]],
    partial_items_plan: List[bool],
) -> Tuple[str, Dict[str, Any]]:
    is_partial = (partial_pharmacy_index is not None and idx == partial_pharmacy_index)

    if is_partial:
        status_label = "PARTIAL"
        publish_body = build_publish_stock_response_body(
            order_number=order_key,
            provider_cufe=pharmacy["cufe"],
            provider_name=pharmacy["name"],
            provider_branch=pharmacy["branch"],
            stock_items=stock_items,
            availability_value=None,
            availability_by_item=partial_items_plan,
        )
        return status_label, publish_body

    status_label = "FULL_STOCK" if is_full else "NO_STOCK"
    publish_body = build_publish_stock_response_body(
        order_number=order_key,
        provider_cufe=pharmacy["cufe"],
        provider_name=pharmacy["name"],
        provider_branch=pharmacy["branch"],
        stock_items=stock_items,
        availability_value=is_full,
        availability_by_item=None,
    )
    return status_label, publish_body


def _print_pharmacies_status(
    pharmacies: List[Dict[str, Any]],
    pharmacies_plan: List[bool],
    partial_pharmacy_index: Optional[int],
) -> None:
    print("\n=== FARMACIAS (NAME -> status) ===")
    for idx, (pharmacy, is_full) in enumerate(zip(pharmacies, pharmacies_plan), start=1):
        status = _status_for_pharmacy(idx - 1, is_full, partial_pharmacy_index)
        print(f"{idx}. {pharmacy['name']} -> {status}")


def _print_publish_block(
    idx: int,
    pharmacy_name: str,
    status_label: str,
    url: str,
    request_payload: Dict[str, Any],
    raw_http: Dict[str, Any],
) -> None:
    """
    Formato requerido:
    -- n. Farmacia (STATUS) --
    URL: ...
    REQUEST (payload):
    {...}
    *********************
    RESPONSE RAW:
    <texto crudo>
    (opcional) JSON pretty si existe
    *********************
    """
    print(f"\n-- {idx}. {pharmacy_name} ({status_label}) --")

    print(f"URL: {url}")
    print("REQUEST (payload):")
    print(_pretty(request_payload))

    print("\n*********************")

    # Preferimos texto crudo si está
    response_text = raw_http.get("text")
    response_json = raw_http.get("json")

    print("RESPONSE RAW:")
    if response_text is not None and str(response_text).strip() != "":
        print(response_text)
    elif response_json is not None:
        print(_pretty(response_json))
    else:
        # fallback: mostrar lo que tengamos sin headers
        minimal = {k: v for k, v in raw_http.items() if k in ("url", "status_code", "text", "json")}
        if minimal:
            print(_pretty(minimal))
        else:
            print(_pretty(raw_http))

    # Si hay JSON, lo mostramos formateado abajo (sin duplicar si ya imprimimos json por falta de text)
    if response_json is not None and (response_text is not None and str(response_text).strip() != ""):
        print("\nRESPONSE JSON (pretty):")
        print(_pretty(response_json))

    print("*********************\n")


def _publish_for_all_pharmacies(
    pharmacies: List[Dict[str, Any]],
    pharmacies_plan: List[bool],
    partial_pharmacy_index: Optional[int],
    partial_items_plan: List[bool],
    order_key: str,
    stock_items: List[Dict[str, Any]],
    web_bearer_token: str,
    trace_id: str,
    timeout_seconds: int,
    delay_seconds: int,
) -> List[Dict[str, Any]]:
    publish_results: List[Dict[str, Any]] = []

    print("\n=== PUBLISH STOCK RESPONSE (RAW) ===")

    for idx0, (pharmacy, is_full) in enumerate(zip(pharmacies, pharmacies_plan)):
        idx_human = idx0 + 1

        status_label, publish_body = _build_publish_body_and_status(
            idx=idx0,
            pharmacy=pharmacy,
            is_full=is_full,
            partial_pharmacy_index=partial_pharmacy_index,
            order_key=order_key,
            stock_items=stock_items,
            partial_items_plan=partial_items_plan,
        )

        raw_http = publish_stock_response(
            PUBLISH_STOCK_RESPONSE_URL,
            web_bearer_token=web_bearer_token,
            trace_id=trace_id,
            body=publish_body,
            timeout_seconds=timeout_seconds,
        )

        # NO headers en consola
        url = raw_http.get("url") or PUBLISH_STOCK_RESPONSE_URL
        _print_publish_block(
            idx=idx_human,
            pharmacy_name=pharmacy["name"],
            status_label=status_label,
            url=url,
            request_payload=publish_body,
            raw_http=raw_http,
        )

        publish_results.append({
            "pharmacyId": pharmacy["pharmacyId"],
            "pharmacyName": pharmacy["name"],
            "statusSent": status_label,
            "http": raw_http,
            "request": publish_body,  # útil si luego querés ver qué mandaste
        })
        
        if delay_seconds > 0 and idx0 < (len(pharmacies) - 1):
            print(f"Esperando {delay_seconds}s para la próxima farmacia...\n")
            time.sleep(delay_seconds)

    return publish_results


def run_erp_stock_flow(
    web_email: str,
    web_password: str,
    sellercenter_username: str,
    sellercenter_password: str,
    order_id: str,
    customer_id: str,
    latitude: float,
    longitude: float,
    items_per_page: int = 5,
    timeout_seconds: int = 30,
    delay_seconds: int = 10,
    force_all_full_stock: bool = False,
    force_all_no_stock: bool = False,
) -> Dict[str, Any]:
    # 1) Tokens
    web_bearer_token, sellercenter_token = _get_tokens(
        web_email=web_email,
        web_password=web_password,
        sellercenter_username=sellercenter_username,
        sellercenter_password=sellercenter_password,
    )

    # 2) Farmacias (ByLocationApp)
    pharmacies = _get_pharmacies(
        sellercenter_token=sellercenter_token,
        customer_id=customer_id,
        latitude=latitude,
        longitude=longitude,
        items_per_page=items_per_page,
    )

    # 3) Request Stock -> TraceId
    trace_id = _get_trace_id(
        web_bearer_token=web_bearer_token,
        order_id=order_id,
        pharmacies=pharmacies,
    )

    # 4) Pedidos Core -> stock-request-data
    order_key, stock_items = _get_order_key_and_items(
        web_bearer_token=web_bearer_token,
        order_id=order_id,
    )

    # 5) Plan farmacias: mitad FULL / mitad NO + 1 PARTIAL con 1 item en False
    if force_all_full_stock:
        pharmacies_plan = [True] * len(pharmacies)
        partial_pharmacy_index = None  # no hacemos PARTIAL en modo "todas FULL"
    elif force_all_no_stock:
        pharmacies_plan = [False] * len(pharmacies)
        partial_pharmacy_index = None  # no hacemos PARTIAL en modo "todas NO"
    else:
        pharmacies_plan = _split_half_true_half_false(len(pharmacies))
        partial_pharmacy_index = _pick_partial_pharmacy_index(pharmacies_plan)

    partial_items_plan = _make_partial_one_item_unavailable(len(stock_items), unavailable_index=0)

    _print_pharmacies_status(
        pharmacies=pharmacies,
        pharmacies_plan=pharmacies_plan,
        partial_pharmacy_index=partial_pharmacy_index,
    )

    publish_results = _publish_for_all_pharmacies(
        pharmacies=pharmacies,
        pharmacies_plan=pharmacies_plan,
        partial_pharmacy_index=partial_pharmacy_index,
        partial_items_plan=partial_items_plan,
        order_key=order_key,
        stock_items=stock_items,
        web_bearer_token=web_bearer_token,
        trace_id=trace_id,
        timeout_seconds=timeout_seconds,
        delay_seconds=delay_seconds
    )

    return {
        "orderId": order_id,
        "orderKey": order_key,
        "traceId": trace_id,
        "pharmaciesCount": len(pharmacies),
        "publishResults": publish_results,
    }