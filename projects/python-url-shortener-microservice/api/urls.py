from django.urls import path

from shortener.views import URLAnalyticsView, URLCreateView

urlpatterns = [
    path("urls/", URLCreateView.as_view(), name="url-create"),
    path("analytics/<slug:short_code>/", URLAnalyticsView.as_view(), name="url-analytics"),
]
