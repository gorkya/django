import json
from urllib import request
import ssl


class JSONRPCClient():
    def __init__(self, endpoint: str, sert: str, key: str):
        self.endpoint = endpoint
        self.cert = sert
        self.key = key

    def call(self, method: str, params: dict) -> dict:
        ssl_context = ssl.create_default_context()
        ssl_context.load_cert_chain(
            self.cert,
            self.key
        )

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
