from django.urls import path

from .views import RedirectView

urlpatterns = [
    path("<str:short_code>/", RedirectView.as_view(), name="redirect"),
]
