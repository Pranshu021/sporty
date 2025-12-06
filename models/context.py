from dataclasses import dataclass
from typing import List

@dataclass
class UserContext:
    leagues_and_tournaments: List[str]
