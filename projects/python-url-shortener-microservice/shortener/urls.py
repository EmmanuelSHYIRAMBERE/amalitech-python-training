from django.urls import path

from .views import RedirectView

urlpatterns = [
    # <slug:short_code> only matches [a-zA-Z0-9_-]+ — rejects "../admin",
    # "<script>", and URL-encoded payloads that <str:> would silently accept.
    path("<slug:short_code>/", RedirectView.as_view(), name="redirect"),
]
