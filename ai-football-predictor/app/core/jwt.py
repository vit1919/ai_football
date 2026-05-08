from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError
from app.utils import get_now_utc

def create_token(user_id: int) -> str:
    now = get_now_utc()

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "iss": "ai-football-app",
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.algorithm]
        )

        return payload
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Auth error")
