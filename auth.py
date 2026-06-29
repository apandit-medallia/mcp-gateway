from dataclasses import dataclass
from fastapi import Request


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


@dataclass
class AuthContext:
    tenant_id: str
    user_id: str
    capabilities: list[str]


def authenticate_and_authorize(
    request: Request,
    required_capability: str | None = None,
) -> AuthContext:
    """
    Expected Authorization header:

    Authorization: Bearer tenant1_user1_tools/list,tools/call

    Token format:
        <tenant_id>_<user_id>_<capabilities>

    Example:
        tenant1_abhishek_tools/list,tools/call

    capabilities are comma separated.
    """

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise AuthenticationError("Missing Authorization header")

    if not auth_header.startswith("Bearer "):
        raise AuthenticationError("Invalid Authorization header")

    token = auth_header[len("Bearer "):].strip()

    parts = token.split("_", 2)

    if len(parts) != 3:
        raise AuthenticationError("Invalid bearer token")

    tenant_id, user_id, capability_string = parts

    capabilities = [
        capability.strip()
        for capability in capability_string.split(",")
        if capability.strip()
    ]

    auth_context = AuthContext(
        tenant_id=tenant_id,
        user_id=user_id,
        capabilities=capabilities,
    )

    if (
        required_capability
        and required_capability not in auth_context.capabilities
    ):
        raise AuthorizationError(
            f"User is not authorized for '{required_capability}'"
        )

    return auth_context