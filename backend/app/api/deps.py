from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db_session

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[Session, Depends(get_db_session)]


def get_tenant_id(
    settings: SettingsDep,
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> str:
    """Resolve a tenant scope.

    The header is a development seam, not authentication. Production deployments
    should populate tenant identity from a verified session or identity token.
    """
    return x_tenant_id or settings.default_tenant_id


TenantDep = Annotated[str, Depends(get_tenant_id)]
