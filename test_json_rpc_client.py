import json
import ssl
import unittest
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError, URLError

from json_rpc_client import JSONRPCClient, JSONRPCError, JSONRPCTransportError


def _fake_response(payload: dict) -> mock.MagicMock:
    response = mock.MagicMock()
    response.read.return_value = json.dumps(payload).encode("utf-8")
    return response


class JSONRPCClientCallTests(unittest.TestCase):
    def setUp(self):
        self.client = JSONRPCClient("https://example.test/api/v2/", "cert", "key")
        # TLS/certs are covered separately in JSONRPCClientTLSTests; here
        # we only care about request building and response parsing.
        patcher = mock.patch.object(
            self.client, "_build_ssl_context", return_value=None
        )
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
            {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": 1,
            }
        )

        with self.assertRaises(JSONRPCError) as ctx:
            self.client.call("does.not.exist", {})

        self.assertIn("Method not found", str(ctx.exception))

    @mock.patch("json_rpc_client.request.urlopen")
    def test_params_defaults_to_empty_dict(self, mock_urlopen):
        mock_urlopen.return_value = _fake_response(
            {"jsonrpc": "2.0", "result": None, "id": 1}
        )

        self.client.call("auth.check")

        sent_request = mock_urlopen.call_args.args[0]
        sent_body = json.loads(sent_request.data.decode("utf-8"))
        self.assertEqual(sent_body["params"], {})

    @mock.patch("json_rpc_client.request.urlopen")
    def test_timeout_is_passed_to_urlopen(self, mock_urlopen):
        mock_urlopen.return_value = _fake_response(
            {"jsonrpc": "2.0", "result": None, "id": 1}
        )

        self.client.call("auth.check")

        self.assertEqual(mock_urlopen.call_args.kwargs["timeout"], self.client.timeout)


class JSONRPCClientTransportErrorTests(unittest.TestCase):
    def setUp(self):
        self.client = JSONRPCClient("https://example.test/api/v2/", "cert", "key")
        patcher = mock.patch.object(
            self.client, "_build_ssl_context", return_value=None
        )
        self.addCleanup(patcher.stop)
        patcher.start()

    @mock.patch("json_rpc_client.request.urlopen")
    def test_http_error_status_raises_transport_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            "https://example.test/api/v2/", 503, "Service Unavailable", {}, None
        )

        with self.assertRaises(JSONRPCTransportError):
            self.client.call("auth.check")

    @mock.patch("json_rpc_client.request.urlopen")
    def test_network_error_raises_transport_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("timed out")

        with self.assertRaises(JSONRPCTransportError):
            self.client.call("auth.check")

    @mock.patch("json_rpc_client.request.urlopen")
    def test_invalid_json_body_raises_transport_error(self, mock_urlopen):
        response = mock.MagicMock()
        response.read.return_value = b"not json"
        mock_urlopen.return_value = response

        with self.assertRaises(JSONRPCTransportError):
            self.client.call("auth.check")

    @mock.patch("json_rpc_client.request.urlopen")
    def test_missing_result_and_error_raises_transport_error(self, mock_urlopen):
        mock_urlopen.return_value = _fake_response({"jsonrpc": "2.0", "id": 1})

        with self.assertRaises(JSONRPCTransportError):
            self.client.call("auth.check")


class JSONRPCClientTLSTests(unittest.TestCase):
    def test_cert_and_key_text_written_to_temp_files_and_loaded(self):
        seen = {}

        def spy_load_cert_chain(self, certfile, keyfile=None, password=None):
            seen["cert"] = Path(certfile).read_text()
            seen["key"] = Path(keyfile).read_text()

        client = JSONRPCClient(
            "https://example.test/", "FAKE-CERT-TEXT", "FAKE-KEY-TEXT"
        )

        with mock.patch.object(ssl.SSLContext, "load_cert_chain", spy_load_cert_chain):
            client._build_ssl_context()

        self.assertEqual(seen["cert"], "FAKE-CERT-TEXT")
        self.assertEqual(seen["key"], "FAKE-KEY-TEXT")


if __name__ == "__main__":
    unittest.main()
