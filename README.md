# mcache-sdk-python

Python SDK for [mcache](https://github.com/mcache-team/mcache) — supports both HTTP and gRPC transports.

## Installation

```bash
pip install mcache-sdk
```

Or from source:

```bash
pip install -e ".[dev]"
```

## Quick Start

### HTTP Client

```python
from mcache.http_client import HttpClient

with HttpClient("http://localhost:8080") as c:
    # insert with 60-second TTL
    c.insert("user/profile/name", "alice", ttl_seconds=60)

    # get by exact prefix
    item = c.get("user/profile/name")
    print(item.data)        # alice
    print(item.created_at)  # datetime

    # update
    c.update("user/profile/name", "bob")

    # list all children under a path
    items = c.list_by_prefix("user/profile")
    for it in items:
        print(it.prefix, it.data)

    # delete
    c.delete("user/profile/name")
```

### gRPC Client

```python
from mcache.grpc_client import GrpcClient

with GrpcClient("localhost:9090") as c:
    c.insert("user/profile/name", {"age": 30}, ttl_seconds=300)

    item = c.get("user/profile/name")
    print(item.data)  # {"age": 30}
```

## API Reference

Both `HttpClient` and `GrpcClient` implement the same `CacheClient` interface:

| Method | Description |
|---|---|
| `insert(prefix, data, *, ttl_seconds=0)` | Create a cache entry. Raises `AlreadyExistsError` if prefix exists. |
| `get(prefix)` | Get entry by exact prefix. Raises `NotFoundError` if missing or expired. |
| `update(prefix, data, *, ttl_seconds=0)` | Update existing entry. Raises `NotFoundError` if missing. |
| `delete(prefix)` | Delete entry. Raises `NotFoundError` if missing. |
| `list_by_prefix(prefix)` | List all direct children under a prefix path. |
| `close()` | Release connections. Called automatically via context manager. |

### Exceptions

| Exception | When |
|---|---|
| `mcache.NotFoundError` | Prefix not found or expired |
| `mcache.AlreadyExistsError` | Duplicate insert |
| `mcache.McacheError` | Other server or transport errors |

### Item fields

```python
@dataclass
class Item:
    prefix: str
    data: Any                        # JSON-deserialized value
    created_at: datetime
    updated_at: datetime
    expire_time: Optional[datetime]  # None if no TTL set
```

## Requirements

- Python >= 3.9
- `requests >= 2.31` (HTTP client)
- `grpcio >= 1.64` (gRPC client)
- `protobuf >= 4.25` (gRPC client)
