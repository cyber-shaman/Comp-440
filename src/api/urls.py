from django.urls import path
from . import api_views

urlpatterns = [
    path('api/signup/', api_views.api_signup),
    path('api/login/', api_views.api_login),
    path('api/add_rental_unit/', api_views.add_rental_unit),
    path('api/search_rental_units/', api_views.search_rental_units),
]