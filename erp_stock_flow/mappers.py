from typing import Any, Dict, List, Tuple, Optional


def extract_order_number_and_items(stock_request_data_json: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Soporta:
    - respuesta directa: { "orderNumber": "...", "items": [...] }
    - wrapper: { "data": { "orderNumber": "...", "items": [...] } }
    """
    payload = stock_request_data_json.get("data") or stock_request_data_json
    order_number = payload["orderKey"]
    items = payload["items"]

    return str(order_number), items


def build_publish_stock_response_body(
    order_number: str,
    provider_cufe: str,
    provider_name: str,
    provider_branch: str,
    stock_items: List[Dict[str, Any]],
    availability_value: Optional[bool] = None,
    availability_by_item: Optional[List[bool]] = None,
) -> Dict[str, Any]:
    """
    - Si availability_by_item viene seteado: availability por ítem (PARTIAL).
    - Si no: availability_value para todos los ítems (FULL/NO).
    - Default: False.
    """
    items_out: List[Dict[str, Any]] = []

    for idx, item in enumerate(stock_items):
        troquel_code = item.get("troquelCode") or item.get("TroquelCode")
        alphabeta_code = item.get("alphabetaCode") or item.get("AlphabetaCode")
        bar_code = item.get("barCode") or item.get("BarCode")
        quantity = item.get("quantity") or item.get("Quantity")

        if troquel_code is None or alphabeta_code is None or bar_code is None or quantity is None:
            raise KeyError(f"Item sin campos esperados. Item: {item}")

        if availability_by_item is not None and len(availability_by_item) > 0:
            # Si por alguna razón la lista no coincide, hacemos wrap
            availability = availability_by_item[idx % len(availability_by_item)]
        else:
            availability = bool(availability_value) if availability_value is not None else False

        items_out.append({
            "troquelCode": str(troquel_code),
            "alphabetaCode": str(alphabeta_code),
            "barCode": str(bar_code),
            "quantity": int(quantity),
            "availability": availability,
        })

    return {
        "orderNumber": order_number,
        "provider": {
            "cufe": provider_cufe,
            "name": provider_name,
            "branch": provider_branch,
        },
        "items": items_out,
    }