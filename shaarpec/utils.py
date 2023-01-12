"""Utils module."""
from typing import Optional, Any

from pydantic import BaseModel


class Debugger(BaseModel):
    """Model used for debugging."""

    payload: Optional[Any]
