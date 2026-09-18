import json
import ssl
import unittest
from pathlib import Path
from unittest import mock

from json_rpc_client import JSONRPCClient


def _fake_response(payload: dict) -> mock.MagicMock:
    response = mock.MagicMock()
    response.read.return_value = json.dumps(payload).encode("utf-8")
    return response


class JSONRPCClientCallTests(unittest.TestCase):
    def setUp(self):
        self.client = JSONRPCClient("https://example.test/api/v2/", "cert", "key")
        # SSL/сертификаты — отдельная забота, проверяется в
        # JSONRPCClientTLSTests. Тут интересует только сборка запроса и
        # разбор ответа, поэтому строим ssl_context не по-настоящему.
        patcher = mock.patch.object(self.client, "_build_ssl_context", return_value=None)
        self.addCleanup(patcher.stop)
        patcher.start()

    @mock.patch("json_rpc_client.request.urlopen")
    def test_successful_call_returns_result(self, mock_urlopen):
        mock_urlopen.return_value = _fake_response(
            {"jsonrpc": "2.0", "result": {"ok": True}, "id": 1}
        )

        result = self.client.call("auth.check", {})

        self.assertEqual(result, {"ok": True})
        sent_request = mock_urlopen.call_args.args[0]
        sent_body = json.loads(sent_request.data.decode("utf-8"))
        self.assertEqual(sent_body["method"], "auth.check")
        self.assertEqual(sent_body["jsonrpc"], "2.0")

    @mock.patch("json_rpc_client.request.urlopen")
    def test_error_response_raises(self, mock_urlopen):
        mock_urlopen.return_value = _fake_response(
            {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": 1}
        )

        with self.assertRaises(Exception) as ctx:
            self.client.call("does.not.exist", {})

        self.assertIn("Method not found", str(ctx.exception))

    @mock.patch("json_rpc_client.request.urlopen")
    def test_params_defaults_to_empty_dict(self, mock_urlopen):
        mock_urlopen.return_value = _fake_response({"jsonrpc": "2.0", "result": None, "id": 1})

        self.client.call("auth.check")

        sent_request = mock_urlopen.call_args.args[0]
        sent_body = json.loads(sent_request.data.decode("utf-8"))
        self.assertEqual(sent_body["params"], {})


class JSONRPCClientTLSTests(unittest.TestCase):
    def test_cert_and_key_text_written_to_temp_files_and_loaded(self):
        seen = {}

        def spy_load_cert_chain(self, certfile, keyfile=None, password=None):
            seen["cert"] = Path(certfile).read_text()
            seen["key"] = Path(keyfile).read_text()

        client = JSONRPCClient("https://example.test/", "FAKE-CERT-TEXT", "FAKE-KEY-TEXT")

        with mock.patch.object(ssl.SSLContext, "load_cert_chain", spy_load_cert_chain):
            client._build_ssl_context()

        self.assertEqual(seen["cert"], "FAKE-CERT-TEXT")
        self.assertEqual(seen["key"], "FAKE-KEY-TEXT")


if __name__ == "__main__":
    unittest.main()