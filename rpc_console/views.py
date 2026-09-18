import json

from django.conf import settings
from django.views.generic.edit import FormView

from .forms import MethodCallForm
from .services import call_method

# __package__ равен "rpc_console" — если приложение переименуют, значение
# обновится само, строку менять не нужно.
INDEX_TEMPLATE_NAME = f"{__package__}/index.html"


class RPCConsoleView(FormView):
    template_name = INDEX_TEMPLATE_NAME
    form_class = MethodCallForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("endpoint", settings.JSONRPC_ENDPOINT)
        return context

    def form_valid(self, form):
        # Не вызываем super().form_valid() — он бы сделал редирект на
        # success_url. Результат вызова нужно показать на этой же
        # странице, поэтому рендерим форму+результат сами.
        context = self.get_context_data(form=form)
        try:
            result = call_method(form.cleaned_data["method"], form.cleaned_data["params"])
        except Exception as exc:
            context["call_error"] = str(exc)
        else:
            context["result_json"] = json.dumps(result, indent=2, ensure_ascii=False)
        return self.render_to_response(context)
