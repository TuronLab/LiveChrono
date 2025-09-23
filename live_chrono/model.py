from dataclasses import dataclass
from typing import Optional


# ---------------- Result Dataclass ----------------
@dataclass
class ChronoResult:
    start_time: float       # absolute UNIX timestamp
    end_time: Optional[float] = None
    elapsed: Optional[float] = None
    elapsed_format: Optional[str] = ""
    display_format: str = ""