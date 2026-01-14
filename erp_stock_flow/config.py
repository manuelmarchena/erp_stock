from dotenv import load_dotenv
import os

load_dotenv()

FT_ENV_STG = os.getenv("FT_ENV_STG", "False").strip().lower() in ("1", "true", "yes", "y", "on")

if FT_ENV_STG:
    BASE_URL = "https://api-staging.farmatouch.com"
    print("Iniciando ejecución en entorno Staging")
else:
    BASE_URL = "https://quality.farmatouch.com"
    print("Iniciando ejecución en entorno Quality")


# Auth
WEB_LOGIN_URL = f"{BASE_URL}/core-security-backend/api/v1/Autentication/SignIn"
SELLERCENTER_LOGIN_URL = f"{BASE_URL}/operation-access-control/api/Autentication/LogIn"

# APIs
BY_LOCATION_APP_URL = f"{BASE_URL}/sellercenter-backend/api/v3/Pharmacy/ByLocationApp"

STOCK_REQUEST_DATA_BASE_URL = f"{BASE_URL}/pedidos-core-backend/api/v1/Order/stock-request-data"
STOCK_REQUEST_DATA_SUFFIX = ""

# Pedidos Core - Customer Address
CUSTOMER_DEFAULT_ADDRESS_URL = (
    f"{BASE_URL}/pedidos-core-backend/api/v1/CustomerAddress/GetCustomerDefaultAddressByCustomerId"
)

REQUEST_STOCK_URL = f"{BASE_URL}/erp-orchestration-api/api/v1/order/request-stock"
PUBLISH_STOCK_RESPONSE_URL = f"{BASE_URL}/erp-integration-api/api/v1/test/publish-stock-response"