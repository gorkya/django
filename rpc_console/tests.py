from unittest import mock

from django.test import SimpleTestCase
from django.urls import reverse

from json_rpc_client import JSONRPCError


class MethodCallFormTests(SimpleTestCase):
    def _form(self, **data):
        from rpc_console.forms import MethodCallForm

        return MethodCallForm(data=data)

    def test_valid_json_object_params(self):
        form = self._form(method="auth.check", params='{"a": 1}')
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["params"], {"a": 1})

    def test_valid_json_array_params(self):
        form = self._form(method="echo", params='["a", 1]')
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["params"], ["a", 1])

    def test_empty_params_defaults_to_empty_dict(self):
        form = self._form(method="auth.check", params="")
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["params"], {})

    def test_invalid_json_is_rejected(self):
        form = self._form(method="auth.check", params="{not json")
        self.assertFalse(form.is_valid())
        self.assertIn("params", form.errors)

    def test_non_object_or_array_json_is_rejected(self):
        form = self._form(method="auth.check", params="42")
        self.assertFalse(form.is_valid())
        self.assertIn("params", form.errors)

    def test_missing_method_is_required(self):
        form = self._form(params="{}")
        self.assertFalse(form.is_valid())
        self.assertIn("method", form.errors)


class RPCConsoleViewTests(SimpleTestCase):
    def setUp(self):
        self.url = reverse("rpc_console:index")

    def test_get_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "JSON-RPC console")

    @mock.patch("rpc_console.views.call_method")
    def test_successful_call_shows_result(self, mock_call_method):
        mock_call_method.return_value = {"ok": True}

        response = self.client.post(self.url, {"method": "auth.check", "params": "{}"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "&quot;ok&quot;: true")
        mock_call_method.assert_called_once_with("auth.check", {})

    @mock.patch("rpc_console.views.call_method")
    def test_call_error_is_displayed(self, mock_call_method):
        mock_call_method.side_effect = JSONRPCError({"code": -32000, "message": "boom"})

        response = self.client.post(self.url, {"method": "auth.check", "params": "{}"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "boom")

    def test_invalid_params_shows_form_error(self):
        response = self.client.post(
            self.url, {"method": "auth.check", "params": "{bad"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Некорректный JSON")
