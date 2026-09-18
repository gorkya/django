import json
from typing import Any

from django.conf import settings
from django.http import HttpResponse
from django.views.generic.edit import FormView

from json_rpc_client import JSONRPCError

from .forms import MethodCallForm
from .services import call_method

# __package__ is "rpc_console" here — survives an app rename automatically.
INDEX_TEMPLATE_NAME = f"{__package__}/index.html"


class RPCConsoleView(FormView):
    template_name = INDEX_TEMPLATE_NAME
    form_class = MethodCallForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.setdefault("endpoint", settings.JSONRPC_ENDPOINT)
        return context

    def form_valid(self, form: MethodCallForm) -> HttpResponse:
        # Skip super().form_valid() — it would redirect to success_url.
        # We render the result on the same page instead.
        context = self.get_context_data(form=form)
        try:
            result = call_method(
                form.cleaned_data["method"], form.cleaned_data["params"]
            )
        except JSONRPCError as exc:
            context["call_error"] = str(exc)
        else:
            context["result_json"] = json.dumps(result, indent=2, ensure_ascii=False)
        return self.render_to_response(context)
