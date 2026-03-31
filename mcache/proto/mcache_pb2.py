# -*- coding: utf-8 -*-
# Hand-written protobuf message stubs for mcache.proto
# Avoids requiring protoc at install time.
# Compatible with grpcio-tools generated interface.

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()

# Minimal descriptor — grpc uses this for serialisation via protobuf runtime.
# We define each message using the proto3 binary wire format helpers.

from google.protobuf import descriptor_pb2 as _dpb2

_PROTO_FILE = _dpb2.FileDescriptorProto()
_PROTO_FILE.name = "mcache.proto"
_PROTO_FILE.package = "mcache"
_PROTO_FILE.syntax = "proto3"

def _msg(name, fields):
    """Helper: build a DescriptorProto."""
    m = _dpb2.DescriptorProto()
    m.name = name
    for number, fname, ftype in fields:
        # ftype: 9=string, 12=bytes, 3=int64, 8=bool, 11=message
        f = m.field.add()
        f.name = fname
        f.number = number
        f.type = ftype
        f.label = 1  # LABEL_OPTIONAL
    return m

# Field type constants (proto FieldDescriptorProto.Type)
_STRING = 9
_BYTES  = 12
_INT64  = 3
_BOOL   = 8
_MSG    = 11

for _m in [
    _msg("InsertRequest",       [(1,"prefix",_STRING),(2,"data",_BYTES),(3,"ttl_seconds",_INT64)]),
    _msg("InsertResponse",      [(1,"success",_BOOL)]),
    _msg("GetRequest",          [(1,"prefix",_STRING)]),
    _msg("GetResponse",         [(1,"prefix",_STRING),(2,"data",_BYTES),(3,"expire_time",_INT64),(4,"created_at",_INT64),(5,"updated_at",_INT64)]),
    _msg("UpdateRequest",       [(1,"prefix",_STRING),(2,"data",_BYTES),(3,"ttl_seconds",_INT64)]),
    _msg("UpdateResponse",      [(1,"success",_BOOL)]),
    _msg("DeleteRequest",       [(1,"prefix",_STRING)]),
    _msg("DeleteResponse",      [(1,"success",_BOOL)]),
    _msg("ListByPrefixRequest", [(1,"prefix",_STRING)]),
]:
    _PROTO_FILE.message_type.append(_m)

# ListByPrefixResponse has a repeated GetResponse field
_lbp = _dpb2.DescriptorProto()
_lbp.name = "ListByPrefixResponse"
_f = _lbp.field.add()
_f.name = "items"
_f.number = 1
_f.type = _MSG
_f.label = 3  # LABEL_REPEATED
_f.type_name = ".mcache.GetResponse"
_PROTO_FILE.message_type.append(_lbp)

_pool = _descriptor_pool.Default()
try:
    _pool.Add(_PROTO_FILE)
except TypeError:
    pass  # already registered

_builder.BuildMessageAndEnumTypes(
    _pool.FindFileByName("mcache.proto"),
    globals(),
    _sym_db,
)

__all__ = [
    "InsertRequest", "InsertResponse",
    "GetRequest", "GetResponse",
    "UpdateRequest", "UpdateResponse",
    "DeleteRequest", "DeleteResponse",
    "ListByPrefixRequest", "ListByPrefixResponse",
]
