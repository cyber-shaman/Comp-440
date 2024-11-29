from django.urls import path
from . import api_views

urlpatterns = [
    path('api/signup/', api_views.api_signup),
    path('api/login/', api_views.api_login),
<<<<<<< Updated upstream
=======
    path('api/add_rental_unit/', api_views.add_rental_unit),
    path('api/search_rental_units/', api_views.search_rental_units),
    path('api/add_review/', api_views.add_review),
>>>>>>> Stashed changes
]