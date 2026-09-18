from json_rpc_client import JSONRPCClient

from django.conf import settings


def call_method(method: str, params: dict | None = None) -> dict:
    return JSONRPCClient(
        endpoint=settings.JSONRPC_ENDPOINT,
        cert_pem=settings.CLIENT_CERT_PEM,
        key_pem=settings.CLIENT_KEY_PEM,
    ).call(method=method, params=params)
