"""A mock service-status page, like status.example.com for the company's IT services."""
from __future__ import annotations

from common.mocks.base import MockService

STATUSES = ("operational", "degraded", "outage", "maintenance")

DEFAULT_STATUSES = {
    "email": "operational",
    "vpn": "operational",
    "wifi": "operational",
    "printer": "operational",
    "sso": "operational",
}

MESSAGES = {
    "operational": "{name} is working normally.",
    "degraded": "{name} is slow or partly unavailable. The IT team is investigating.",
    "outage": "{name} is down for everyone. The IT team is working on a fix; no action is needed from users.",
    "maintenance": "{name} is down for planned maintenance until 18:00 today.",
}


class StatusAPI(MockService):
    """Reports whether each IT service is up.

    ``StatusAPI(statuses={"vpn": "outage"})`` overrides the defaults for a test or demo.
    """

    def __init__(self, statuses: dict[str, str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self._statuses = dict(DEFAULT_STATUSES)
        for service, status in (statuses or {}).items():
            self.set_status(service, status)

    def set_status(self, service: str, status: str) -> None:
        """Change a service's status (test setup; not logged as a call)."""
        if status not in STATUSES:
            raise ValueError(f"Unknown status {status!r}. Choose one of {STATUSES}.")
        self._statuses[service.strip().lower()] = status

    def check_status(self, service: str) -> dict:
        self._begin("check_status", {"service": service})
        name = service.strip().lower()
        if name not in self._statuses:
            known = ", ".join(sorted(self._statuses))
            return {
                "service": name,
                "status": "unknown",
                "message": f"There is no service called {name!r}. Known services: {known}.",
            }
        status = self._statuses[name]
        return {"service": name, "status": status, "message": MESSAGES[status].format(name=name.upper())}
