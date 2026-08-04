from django.urls import path

from .views import PreviewFetchView, PreviewHealthView

urlpatterns = [
    path("preview/fetch/", PreviewFetchView.as_view(), name="preview-fetch"),
    path("preview/health/", PreviewHealthView.as_view(), name="preview-health"),
]
