from django.urls import path
from . import api_views

urlpatterns = [
    path('api/signup/', api_views.api_signup),
    path('api/login/', api_views.api_login),
]