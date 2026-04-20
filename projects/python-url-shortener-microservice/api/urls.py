from django.urls import path
from shortener.views import URLCreateView

urlpatterns = [
    path("urls/", URLCreateView.as_view(), name="url-create"),
]
