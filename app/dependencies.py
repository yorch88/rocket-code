from fastapi import Header, HTTPException, status
from .config import get_settings

s = get_settings()

async def require_api_key(x_api_key: str | None = Header(default=None)):
    if s.API_KEY and x_api_key != s.API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or missing API key")
