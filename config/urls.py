from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("rpc_console/", include("rpc_console.urls")),
    path("admin/", admin.site.urls),
]
