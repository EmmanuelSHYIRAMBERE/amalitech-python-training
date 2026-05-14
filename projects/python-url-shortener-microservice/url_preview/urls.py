from django.urls import path

from .views import PreviewFetchView, PreviewHealthView

urlpatterns = [
    path("fetch/",  PreviewFetchView.as_view(),  name="preview-fetch"),
    path("health/", PreviewHealthView.as_view(), name="preview-health"),
]
