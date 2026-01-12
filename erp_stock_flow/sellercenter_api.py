import requests
from typing import Any, Dict, List


def get_pharmacies_by_location_app(
    by_location_url: str,
    sellercenter_token: str,
    customer_id: str,
    latitude: float,
    longitude: float,
    page_number: int = 1,
    items_per_page: int = 5,
    distance_range: int = 100000,
    timeout_seconds: int = 30,
) -> List[Dict[str, Any]]:
    params = {
        "pageNumber": page_number,
        "itemsPerPage": items_per_page,
        "customerId": customer_id,
        "latitude": latitude,
        "longitude": longitude,
        "openNow": "false",
        "homeDelivery": "false",
        "onlinePayment": "false",
        "onlyActive": "true",
        "distanceRange": distance_range,
        "sortByDistance": "true",
    }

    headers = {
        "accept": "application/json",
        "accept-language": "es-ES,es;q=0.9",
        "access-control-allow-origin": "*",
        "authorization": f"Bearer {sellercenter_token}",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
    }

    response = requests.get(by_location_url, params=params, headers=headers, timeout=timeout_seconds)
    if not response.ok:
        print("BYLOCATION STATUS:", response.status_code)
        print("BYLOCATION TEXT:", response.text[:1200])
        response.raise_for_status()

    payload = response.json()
    pharmacies = payload["result"]["pharmacies"]

    pharmacies_list: List[Dict[str, Any]] = []
    for pharmacy in pharmacies:
        pharmacies_list.append({
            "pharmacyId": pharmacy.get("id"),
            "cufe": pharmacy.get("cufe"),
            "name": pharmacy.get("fantasyName"),
            "branch": pharmacy.get("address"),
        })

    return pharmacies_list