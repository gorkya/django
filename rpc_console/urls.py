from django.urls import path

from rpc_console import views

urlpatterns = [
    path("", views.index, name="index"),
    path("test", views.json_rpc_client_test)
]