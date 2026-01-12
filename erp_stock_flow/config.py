QUALITY_BASE = "https://quality.farmatouch.com"

# Auth
WEB_LOGIN_URL = f"{QUALITY_BASE}/core-security-backend/api/v1/Autentication/SignIn"
SELLERCENTER_LOGIN_URL = f"{QUALITY_BASE}/operation-access-control/api/Autentication/LogIn"

# APIs
BY_LOCATION_APP_URL = f"{QUALITY_BASE}/sellercenter-backend/api/v3/Pharmacy/ByLocationApp"

STOCK_REQUEST_DATA_BASE_URL = f"{QUALITY_BASE}/pedidos-core-backend/api/v1/Order/stock-request-data"
STOCK_REQUEST_DATA_SUFFIX = ""

REQUEST_STOCK_URL = f"{QUALITY_BASE}/erp-orchestration-api/api/v1/order/request-stock"
PUBLISH_STOCK_RESPONSE_URL = f"{QUALITY_BASE}/erp-integration-api/api/v1/test/publish-stock-response"