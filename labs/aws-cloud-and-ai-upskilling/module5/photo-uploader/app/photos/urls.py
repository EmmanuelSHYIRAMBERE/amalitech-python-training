from django.urls import path

from .views import PhotoListCreateView

urlpatterns = [path("", PhotoListCreateView.as_view(), name="photo-list-create")]
