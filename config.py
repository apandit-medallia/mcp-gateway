from qouta_counter import QuotaCounter
from rate_limiter import RateLimiter, RateLimitMode

## Functional MCPs - Integrations, Reporting
## Admin MCPs - Auth, Billing, Alerts
MCP_SERVERS = [
    "http://localhost:8001/mcp",
    "http://localhost:8002/mcp"
]

QOUTA_COUNTER = QuotaCounter(quota=10)

RATE_LIMITER = RateLimiter(
    max_requests=5,
    window_seconds=10,
    mode=RateLimitMode.REJECT,
)

TOOL_ROUTES = {}

TOOL_LIST = []