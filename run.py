import os
import json
from dotenv import load_dotenv

load_dotenv()  

from erp_stock_flow.flow_runner import run_erp_stock_flow


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Falta la variable de entorno: {name}")
    return value


# ====== Credenciales / Inputs ======
FT_WEB_EMAIL = _require_env("FT_WEB_EMAIL")
FT_WEB_PASSWORD = _require_env("FT_WEB_PASSWORD")

FT_SC_USERNAME = _require_env("FT_SC_USERNAME")
FT_SC_PASSWORD = _require_env("FT_SC_PASSWORD")

FT_ORDER_ID = _require_env("FT_ORDER_ID")

FT_CUSTOMER_ID = _require_env("FT_CUSTOMER_ID")
FT_LAT = float(_require_env("FT_LAT"))
FT_LNG = float(_require_env("FT_LNG"))

# Opcionales
FT_ITEMS_PER_PAGE = int(os.getenv("FT_ITEMS_PER_PAGE", "5"))
FT_AVAILABILITY = os.getenv("FT_AVAILABILITY", "false").strip().lower() in ("1", "true", "yes", "y")

FT_FARMA_ACCESS_TOKEN = os.getenv("FT_FARMA_ACCESS_TOKEN")
FT_COOKIES = os.getenv("FT_COOKIES")   

FT_FORCE_ALL_FULL_STOCK = os.getenv("FT_FORCE_ALL_FULL_STOCK", "").strip().lower() in ("1", "true", "yes", "y")
FT_FORCE_ALL_NO_STOCK   = os.getenv("FT_FORCE_ALL_NO_STOCK", "").strip().lower() in ("1", "true", "yes", "y")


# AWAIT
FT_DELAY_SECONDS = int(os.getenv("FT_DELAY_SECONDS", "10"))
# ====== Ejecutar flujo ======
result = run_erp_stock_flow(
    web_email=FT_WEB_EMAIL,
    web_password=FT_WEB_PASSWORD,
    sellercenter_username=FT_SC_USERNAME,
    sellercenter_password=FT_SC_PASSWORD,
    order_id=FT_ORDER_ID,
    customer_id=FT_CUSTOMER_ID,
    latitude=FT_LAT,
    longitude=FT_LNG,
    items_per_page=FT_ITEMS_PER_PAGE,
    delay_seconds=FT_DELAY_SECONDS,
    force_all_full_stock=FT_FORCE_ALL_FULL_STOCK,
    force_all_no_stock=FT_FORCE_ALL_NO_STOCK
)

# print(json.dumps(result, indent=2, ensure_ascii=False))