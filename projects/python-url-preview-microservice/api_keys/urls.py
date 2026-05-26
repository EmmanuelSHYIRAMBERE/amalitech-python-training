from django.urls import path

from .views import APIKeyListCreateView, APIKeyRevokeView

urlpatterns = [
    path("", APIKeyListCreateView.as_view(), name="api-keys-list"),
    path("<int:pk>/revoke/", APIKeyRevokeView.as_view(), name="api-keys-revoke"),
]
