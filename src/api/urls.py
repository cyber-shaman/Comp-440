from django.urls import path
from . import api_views

urlpatterns = [
    path('api/signup/', api_views.api_signup),
    path('api/login/', api_views.api_login),
    path('api/add_rental_unit/', api_views.add_rental_unit),
    path('api/search_rental_units/', api_views.search_rental_units),
    path('api/most_expensive_rental_units/', api_views.most_expensive_rental_units),  # API endpoint for fetching data
    path('api/most_expensive/', api_views.most_expensive_rentals_view),  # Template rendering for the page
    path('api/two_rentals_with_features/', api_views.rentals_with_features_view),
    path('api/rentals_with_positive_reviews/', api_views.rentals_with_positive_reviews),
    path('api/most_rentals_on_date/', api_views.most_rentals_on_date),
    path('api/users_with_only_poor_reviews/', api_views.users_with_only_poor_reviews),
    path('api/users_with_no_poor_reviews/', api_views.users_with_no_poor_reviews),
]
