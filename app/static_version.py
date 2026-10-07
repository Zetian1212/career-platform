from __future__ import annotations
import hashlib
from pathlib import Path

STATIC_DIR = Path('app/static')


def static_version(relative_path: str) -> str:
    """Short content hash for a static file, used to bust browser caches after a deploy."""
    try:
        return hashlib.sha256((STATIC_DIR / relative_path).read_bytes()).hexdigest()[:10]
    except OSError:
        return '0'
