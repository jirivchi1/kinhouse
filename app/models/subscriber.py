"""Modelo de suscriptores a la newsletter (persistencia en un archivo JSON)."""
import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class InvalidEmailError(ValueError):
    pass


class SubscriberRepository:
    _lock = threading.Lock()

    def __init__(self, data_dir: Path):
        self.path = Path(data_dir) / "subscribers.json"

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def add(self, email: str) -> bool:
        """Guarda el email. Devuelve False si ya estaba suscrito."""
        email = (email or "").strip().lower()
        if not EMAIL_RE.match(email):
            raise InvalidEmailError(email)

        with self._lock:
            subscribers = self._load()
            if any(s["email"] == email for s in subscribers):
                return False
            subscribers.append({
                "email": email,
                "subscribed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(subscribers, indent=2), encoding="utf-8")
        return True
