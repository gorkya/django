import json
import tempfile
from pathlib import Path
from urllib import error, request
import ssl

DEFAULT_TIMEOUT = 10


class JSONRPCClientError(Exception):
    """Base for any failure calling the RPC service."""


class JSONRPCError(JSONRPCClientError):
    """The service answered with a JSON-RPC error object."""


class JSONRPCTransportError(JSONRPCClientError):
    """Network, HTTP status, or invalid response body."""


class JSONRPCClient:
    def __init__(
        self,
        endpoint: str,
        cert_pem: str,
        key_pem: str,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.endpoint = endpoint
        self.cert_pem = cert_pem
        self.key_pem = key_pem
        self.timeout = timeout

    def _build_ssl_context(self) -> ssl.SSLContext:
        ssl_context = ssl.create_default_context()
        with tempfile.TemporaryDirectory() as tmp_dir:
            cert_path = Path(tmp_dir) / "client.crt"
            key_path = Path(tmp_dir) / "client.key"
            cert_path.write_text(self.cert_pem)
            key_path.write_text(self.key_pem)
            ssl_context.load_cert_chain(cert_path, key_path)
        # load_cert_chain parses the cert/key immediately, so the temp
        # files can be removed right away — ssl_context no longer needs
        # them on disk after this point.
        return ssl_context

    def call(self, method: str, params: dict | list | None = None) -> dict:
        if params is None:
            params = {}

        ssl_context = self._build_ssl_context()

        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        body = json.dumps(payload).encode("utf-8")

        r = request.Request(
            url=self.endpoint,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )

        try:
            response = request.urlopen(r, context=ssl_context, timeout=self.timeout)
        except error.HTTPError as exc:
            raise JSONRPCTransportError(f"HTTP {exc.code}: {exc.reason}") from exc
        except error.URLError as exc:
            raise JSONRPCTransportError(str(exc.reason)) from exc

        try:
            result_dict = json.loads(response.read())
        except json.JSONDecodeError as exc:
            raise JSONRPCTransportError("invalid JSON in response") from exc

        if "error" in result_dict:
            raise JSONRPCError(result_dict["error"])
        try:
            return result_dict["result"]
        except KeyError as exc:
            raise JSONRPCTransportError("response has no 'result' field") from exc
