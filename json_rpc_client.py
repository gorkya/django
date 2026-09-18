import json
import tempfile
from pathlib import Path
from urllib import request
import ssl


class JSONRPCClient:
    def __init__(self, endpoint: str, cert_pem: str, key_pem: str):
        self.endpoint = endpoint
        self.cert_pem = cert_pem
        self.key_pem = key_pem

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

    def call(self, method: str, params: dict = None) -> dict:
        if params is None:
            params = {}

        ssl_context = self._build_ssl_context()

        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        body = json.dumps(payload).encode('utf-8')

        r = request.Request(
            url=self.endpoint,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"}
        )

        result = request.urlopen(
            r,
            context=ssl_context,
        )

        result_dict = json.loads(result.read())

        if "error" in result_dict:
            raise Exception(f'JSON-RPC error: {result_dict["error"]}')
        return result_dict["result"]


if __name__ == "__main__":
    client = JSONRPCClient(
        'https://slb.medv.ru/api/v2/',
        '/Users/gorkya/Downloads/client2026test.crt',
        '/Users/gorkya/Downloads/client2026test.key'
    )
    print(client.call("auth.check", {}))
