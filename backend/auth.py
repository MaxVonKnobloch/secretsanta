import logging
from typing import Optional

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

credentials = {
    "admin": "admin",
    "max": "max",
    "anka": "anka",
    "mama": "mama",
    "papa": "papa",
    "katharina": "katharina",
    "christoph": "christoph"
}


def get_token_user(token: str) -> Optional[str]:
    """Return the user associated with the given token, or None if not found."""
    for user, user_token in credentials.items():
        if token == user_token:
            return user
    return None


def user_is_allowed_to_access(token: str, admin_only: bool = True, allow_users: Optional[list[str]] = None) -> tuple[
    bool, str]:
    """Check if the provided token is valid. Returns are the user and if the user is allowed to access the site"""
    token_user = get_token_user(token)

    if token_user is None:
        logging.warning("Invalid token attempt, token not found in credentials.")
        return False, ""

    if token_user is not None:
        if admin_only and token_user == "admin":
            logging.info("Admin access granted.")
            return True, "admin"

        if allow_users is None or token_user in allow_users:
            logging.info(f"Access granted for user '{token_user}'.")
            return True, token_user

    return False, ""


def set_token_and_user_in_cookies(request: Request, token_param: str, user: str) -> RedirectResponse:
    clean_url = str(request.url).replace(f"token={token_param}", "").rstrip("&?")
    if "?" in clean_url and clean_url.endswith("?"):
        clean_url = clean_url[:-1]
    resp = RedirectResponse(clean_url or "/")
    resp.set_cookie(
        key="APP_TOKEN",
        value=token_param,
        httponly=True,
        samesite="lax",
        secure=False,  # True if you serve over HTTPS
        max_age=60 * 60 * 24 * 30,  # 30 days
    )
    resp.set_cookie(
        key="APP_USER",
        value=user,
        httponly=False,
        samesite="lax",
        secure=False,  # True if you serve over HTTPS
        max_age=60 * 60 * 24 * 30,  # 30 days
    )

    return resp


async def token_cookie_guard(request: Request, call_next, admin_only: bool = True,
                             protected_route_prefixes: Optional[tuple[str]] = None,
                             allow_users: Optional[list[str]] = None):
    logging.info(f"token_cookie_guard called for path: {request.url.path}")

    # check token in url
    token_param = request.query_params.get("token")

    if token_param is not None:
        logging.info(f"Token param found: {token_param}")
        allowed, user = user_is_allowed_to_access(token=token_param, admin_only=admin_only, allow_users=allow_users)
        logging.info(f"Allowed: {allowed}, User: {user}")
        if allowed:
            logging.info("Token is valid, setting cookies.")
            return set_token_and_user_in_cookies(request, token_param=token_param, user=user)
        logging.warning("Invalid token, raising HTTPException.")
        raise HTTPException(status_code=401, detail="Invalid token")

    # 2) Require cookie for protected paths
    if protected_route_prefixes is None:
        protected_route_prefixes = ("/",)

    if request.url.path.startswith(protected_route_prefixes):
        logging.info(f"Protected path accessed: {request.url.path}")
        token_cookie = request.cookies.get("APP_TOKEN")
        allowed, user = user_is_allowed_to_access(token=token_cookie, admin_only=admin_only, allow_users=allow_users)
        logging.info(f"Cookie allowed: {allowed}, User: {user}")
        if allowed:
            logging.info("Cookie is valid, attaching user to request.state.")
            request.state.user = user  # Attach user to request.state
            request.state.is_superuser = (user == "admin")
            return await call_next(request)
        logging.warning("Unauthorized access, returning JSONResponse.")
        return JSONResponse(
            {"detail": "Unauthorized. Append ?token=YOUR_SECRET to the URL."},
            status_code=401
        )

    return await call_next(request)
