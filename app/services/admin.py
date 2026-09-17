import hashlib
import hmac
from app.config import get_settings

settings = get_settings()


def _token(username: str) -> str:
    payload = f"{username}:{settings.session_secret}".encode('utf-8')
    return hmac.new(settings.session_secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()


def is_authenticated(request) -> bool:
    username = request.cookies.get('admin_user')
    token = request.cookies.get('admin_session')
    if not username or not token:
        return False
    return hmac.compare_digest(username, settings.admin_username) and hmac.compare_digest(token, _token(username))


def require_admin(request) -> None:
    if not is_authenticated(request):
        raise PermissionError('admin required')
