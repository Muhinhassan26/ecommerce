from functools import wraps

from fastapi import HTTPException, Request, status
from src.core.db import get_conn


def check_user_perm(allowed_roles: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user_id = request.state.user["id"]

            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, role FROM users WHERE id = %s", (user_id,))
                    user = cur.fetchone()

                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                    )
                if user["role"] not in allowed_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
                    )
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
