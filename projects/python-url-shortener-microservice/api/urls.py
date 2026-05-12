from django.urls import include, path

from shortener.views import URLAnalyticsView, URLCreateView, URLDetailView, URLListView

urlpatterns = [
    path("auth/", include("users.urls")),
    path("urls/", URLCreateView.as_view(), name="url-create"),
    path("urls/list/", URLListView.as_view(), name="url-list"),
    path("urls/<slug:short_code>/", URLDetailView.as_view(), name="url-detail"),
    path(
        "analytics/<slug:short_code>/", URLAnalyticsView.as_view(), name="url-analytics"
    ),
]
