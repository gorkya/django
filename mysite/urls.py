from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("client/", include("client.urls")),
    path("admin/", admin.site.urls),
]
