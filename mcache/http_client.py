"""HTTP-based mcache client using the REST API."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import quote, urlencode

import requests
from requests import Response, Session

from mcache import AlreadyExistsError, CacheClient, Item, McacheError, NotFoundError


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    # Handle Go's zero time
    if value.startswith("0001-"):
        return None
    try:
        # Go emits RFC3339 with nanoseconds; Python's fromisoformat handles up to microseconds
        value = value[:26] + "Z" if len(value) > 26 else value
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _item_from_dict(d: dict) -> Item:
    return Item(
        prefix=d.get("prefix", ""),
        data=d.get("data"),
        created_at=_parse_dt(d.get("createdAt")) or datetime.now(timezone.utc),
        updated_at=_parse_dt(d.get("UpdatedAt")) or datetime.now(timezone.utc),
        expire_time=_parse_dt(d.get("expireTime")),
    )


class HttpClient(CacheClient):
    """Communicates with mcache over HTTP REST.

    Args:
        base_url: Server base URL, e.g. ``"http://localhost:8080"``.
        timeout: Request timeout in seconds (default 10).
        session: Optional custom :class:`requests.Session`.

    Example::

        from mcache.http_client import HttpClient

        with HttpClient("http://localhost:8080") as c:
            c.insert("user/name", "alice", ttl_seconds=60)
            item = c.get("user/name")
            print(item.data)  # alice
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        session: Optional[Session] = None,
    ) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout
        self._session = session or Session()

    # ------------------------------------------------------------------ #
    # CacheClient interface
    # ------------------------------------------------------------------ #

    def insert(self, prefix: str, data: Any, *, ttl_seconds: float = 0) -> None:
        body: dict = {"prefix": prefix, "data": data}
        if ttl_seconds > 0:
            # server expects nanoseconds in the timeout field
            body["timeout"] = int(ttl_seconds * 1_000_000_000)
        resp = self._request("PUT", "/v1/data", json=body)
        if resp.status_code == 201:
            return
        if resp.status_code == 409:
            raise AlreadyExistsError(f"prefix already exists: {prefix!r}")
        self._raise_for(resp)

    def get(self, prefix: str) -> Item:
        resp = self._request("GET", f"/v1/data/{quote(prefix, safe='')}")
        if resp.status_code == 404:
            raise NotFoundError(f"not found: {prefix!r}")
        if resp.status_code != 200:
            self._raise_for(resp)
        return _item_from_dict(resp.json())

    def update(self, prefix: str, data: Any, *, ttl_seconds: float = 0) -> None:
        body: dict = {"data": data}
        if ttl_seconds > 0:
            body["timeout"] = int(ttl_seconds * 1_000_000_000)
        resp = self._request("POST", f"/v1/data/{quote(prefix, safe='')}", json=body)
        if resp.status_code == 200:
            return
        if resp.status_code == 404:
            raise NotFoundError(f"not found: {prefix!r}")
        self._raise_for(resp)

    def delete(self, prefix: str) -> None:
        resp = self._request("DELETE", f"/v1/data/{quote(prefix, safe='')}")
        if resp.status_code == 200:
            return
        if resp.status_code == 404:
            raise NotFoundError(f"not found: {prefix!r}")
        self._raise_for(resp)

    def list_by_prefix(self, prefix: str) -> list[Item]:
        qs = urlencode({"prefix": prefix})
        resp = self._request("GET", f"/v1/data/listByPrefix?{qs}")
        if resp.status_code != 200:
            self._raise_for(resp)
        raw = resp.json()
        if not raw:
            return []
        return [_item_from_dict(d) for d in raw]

    def close(self) -> None:
        self._session.close()

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _request(self, method: str, path: str, **kwargs: Any) -> Response:
        url = self._base + path
        kwargs.setdefault("timeout", self._timeout)
        return self._session.request(method, url, **kwargs)

    @staticmethod
    def _raise_for(resp: Response) -> None:
        try:
            msg = resp.json().get("message", resp.text)
        except (json.JSONDecodeError, AttributeError):
            msg = resp.text
        raise McacheError(f"mcache http {resp.status_code}: {msg}")
