from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("", include("core.urls")),
    path("api/v1/", include("api.urls")),
    path("api/schema/", SpectacularAPIView.as_view(permission_classes=[]), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[]),
        name="swagger-ui",
    ),
    path("", include("shortener.urls")),
]
