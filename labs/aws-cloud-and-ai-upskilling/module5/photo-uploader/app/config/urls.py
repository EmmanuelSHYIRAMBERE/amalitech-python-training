from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView

from static_site.urls import urlpatterns as static_urlpatterns

urlpatterns = [
    *static_urlpatterns,
    path("health", include("core.urls")),  # NOTE: no trailing slash
    path("api/v1/photos", include("photos.urls")),  # NOTE: no trailing slash
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
]

handler404 = "core.views.not_found_view"
