from django.urls import path

from rpc_console.views import RPCConsoleView

app_name = "rpc_console"

urlpatterns = [
    path("", RPCConsoleView.as_view(), name="index"),
]
