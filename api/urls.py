from django.urls import path

from .views import Comixify, ComixifyImg,ComixifyFromYoutube

urlpatterns = [
    path(r'', Comixify.as_view(), name='comixify'),
    path(r'', ComixifyImg.as_view(), name='comixifyImg'),
    path(r'from_yt/', ComixifyFromYoutube.as_view(), name='comixify_from_yt'),
]
