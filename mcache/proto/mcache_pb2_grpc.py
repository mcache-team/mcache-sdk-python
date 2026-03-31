# -*- coding: utf-8 -*-
# Hand-written gRPC stub for mcache.CacheService

import grpc
from mcache.proto import mcache_pb2 as _pb


class CacheServiceStub:
    """Client stub for mcache.CacheService."""

    def __init__(self, channel: grpc.Channel) -> None:
        self.Insert = channel.unary_unary(
            "/mcache.CacheService/Insert",
            request_serializer=_pb.InsertRequest.SerializeToString,
            response_deserializer=_pb.InsertResponse.FromString,
        )
        self.Get = channel.unary_unary(
            "/mcache.CacheService/Get",
            request_serializer=_pb.GetRequest.SerializeToString,
            response_deserializer=_pb.GetResponse.FromString,
        )
        self.Update = channel.unary_unary(
            "/mcache.CacheService/Update",
            request_serializer=_pb.UpdateRequest.SerializeToString,
            response_deserializer=_pb.UpdateResponse.FromString,
        )
        self.Delete = channel.unary_unary(
            "/mcache.CacheService/Delete",
            request_serializer=_pb.DeleteRequest.SerializeToString,
            response_deserializer=_pb.DeleteResponse.FromString,
        )
        self.ListByPrefix = channel.unary_unary(
            "/mcache.CacheService/ListByPrefix",
            request_serializer=_pb.ListByPrefixRequest.SerializeToString,
            response_deserializer=_pb.ListByPrefixResponse.FromString,
        )
