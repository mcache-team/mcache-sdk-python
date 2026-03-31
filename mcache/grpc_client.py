"""gRPC-based mcache client."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

import grpc
from grpc import Channel

from mcache import AlreadyExistsError, CacheClient, Item, McacheError, NotFoundError
from mcache.proto import mcache_pb2 as _pb
from mcache.proto.mcache_pb2_grpc import CacheServiceStub


def _from_response(r: _pb.GetResponse) -> Item:  # type: ignore[name-defined]
    data: Any
    try:
        data = json.loads(r.data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        data = r.data.decode("utf-8", errors="replace")

    expire_time: Optional[datetime] = None
    if r.expire_time > 0:
        expire_time = datetime.fromtimestamp(r.expire_time, tz=timezone.utc)

    return Item(
        prefix=r.prefix,
        data=data,
        created_at=datetime.fromtimestamp(r.created_at, tz=timezone.utc),
        updated_at=datetime.fromtimestamp(r.updated_at, tz=timezone.utc),
        expire_time=expire_time,
    )


def _map_error(exc: grpc.RpcError, prefix: str) -> McacheError:
    code = exc.code()  # type: ignore[union-attr]
    if code == grpc.StatusCode.NOT_FOUND:
        return NotFoundError(f"not found: {prefix!r}")
    if code == grpc.StatusCode.ALREADY_EXISTS:
        return AlreadyExistsError(f"prefix already exists: {prefix!r}")
    return McacheError(f"mcache grpc {code}: {exc.details()}")  # type: ignore[union-attr]


class GrpcClient(CacheClient):
    """Communicates with mcache over gRPC.

    Args:
        address: Server address, e.g. ``"localhost:9090"``.
        channel: Optional pre-built :class:`grpc.Channel` (overrides *address*).
        options: gRPC channel options list.

    Example::

        from mcache.grpc_client import GrpcClient

        with GrpcClient("localhost:9090") as c:
            c.insert("user/name", "alice", ttl_seconds=60)
            item = c.get("user/name")
            print(item.data)  # alice
    """

    def __init__(
        self,
        address: str = "localhost:9090",
        *,
        channel: Optional[Channel] = None,
        options: Optional[list] = None,
    ) -> None:
        self._owned = channel is None
        self._channel: Channel = channel or grpc.insecure_channel(
            address, options=options or []
        )
        self._stub = CacheServiceStub(self._channel)

    # ------------------------------------------------------------------ #
    # CacheClient interface
    # ------------------------------------------------------------------ #

    def insert(self, prefix: str, data: Any, *, ttl_seconds: float = 0) -> None:
        req = _pb.InsertRequest(
            prefix=prefix,
            data=json.dumps(data).encode(),
            ttl_seconds=int(ttl_seconds),
        )
        try:
            self._stub.Insert(req)
        except grpc.RpcError as e:
            raise _map_error(e, prefix) from e

    def get(self, prefix: str) -> Item:
        req = _pb.GetRequest(prefix=prefix)
        try:
            resp = self._stub.Get(req)
        except grpc.RpcError as e:
            raise _map_error(e, prefix) from e
        return _from_response(resp)

    def update(self, prefix: str, data: Any, *, ttl_seconds: float = 0) -> None:
        req = _pb.UpdateRequest(
            prefix=prefix,
            data=json.dumps(data).encode(),
            ttl_seconds=int(ttl_seconds),
        )
        try:
            self._stub.Update(req)
        except grpc.RpcError as e:
            raise _map_error(e, prefix) from e

    def delete(self, prefix: str) -> None:
        req = _pb.DeleteRequest(prefix=prefix)
        try:
            self._stub.Delete(req)
        except grpc.RpcError as e:
            raise _map_error(e, prefix) from e

    def list_by_prefix(self, prefix: str) -> list[Item]:
        req = _pb.ListByPrefixRequest(prefix=prefix)
        try:
            resp = self._stub.ListByPrefix(req)
        except grpc.RpcError as e:
            raise _map_error(e, prefix) from e
        return [_from_response(r) for r in resp.items]

    def close(self) -> None:
        if self._owned:
            self._channel.close()
