from typing import Optional

from pydantic import BaseModel


class Account(BaseModel):
    session_file: str
    phone: str
    app_id: int
    app_hash: str
    username: Optional[str] = None
    proxy: Optional[str] = None
