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

# Opcionales
FT_ITEMS_PER_PAGE = int(os.getenv("FT_ITEMS_PER_PAGE", "5"))

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
    items_per_page=FT_ITEMS_PER_PAGE,
    delay_seconds=FT_DELAY_SECONDS,
)

# Si querés ver el JSON final completo:
# print(json.dumps(result, indent=2, ensure_ascii=False))
