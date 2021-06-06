from typing import Optional

from models.basic import AbstractModel


class Genre(AbstractModel):
    name: str
    description: Optional[str]
