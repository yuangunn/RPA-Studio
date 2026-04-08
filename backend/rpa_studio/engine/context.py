from __future__ import annotations
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from rpa_studio.models import Step


@dataclass
class ExecutionContext:
    variables: dict[str, Any] = field(default_factory=dict)
    running: bool = True
    current_step: Optional[Step] = None
    log: list[str] = field(default_factory=list)
    error: Optional[str] = None
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def resolve(self, text: str) -> str:
        def replace_match(m: re.Match) -> str:
            key = m.group(1)
            return str(self.variables.get(key, m.group(0)))
        return re.sub(r"\{(\w+)\}", replace_match, str(text))

    def add_log(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.append(f"[{ts}] {message}")

    def save_log_to_disk(self, project_name: str) -> Path:
        log_dir = Path.home() / ".rpa_studio" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in project_name)
        log_path = log_dir / f"{ts}_{safe_name}.log"
        log_path.write_text("\n".join(self.log), encoding="utf-8")
        return log_path
