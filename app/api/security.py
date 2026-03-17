from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.observability.context import bind_actor_subject
from app.settings import get_settings


class AuthContext(BaseModel):
    subject: str
    permissions: frozenset[str] = Field(default_factory=frozenset)

    def has_permission(self, permission: str) -> bool:
        return "*" in self.permissions or permission in self.permissions


def get_current_actor(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> AuthContext:
    settings = get_settings()

    if not settings.auth_enabled:
        actor = AuthContext(subject="dev-bypass", permissions=frozenset({"*"}))
        request.state.actor_subject = actor.subject
        bind_actor_subject(actor.subject)
        return actor

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must use Bearer token auth",
        )

    token_config = settings.auth_tokens.get(token.strip())
    if token_config is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token",
        )

    actor = AuthContext(
        subject=token_config.subject,
        permissions=frozenset(token_config.permissions),
    )
    request.state.actor_subject = actor.subject
    bind_actor_subject(actor.subject)
    return actor


def require_permissions(*permissions: str):
    def dependency(actor: AuthContext = Depends(get_current_actor)) -> AuthContext:
        missing_permissions = [
            permission for permission in permissions if not actor.has_permission(permission)
        ]
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission(s): {', '.join(missing_permissions)}",
            )
        return actor

    return dependency
