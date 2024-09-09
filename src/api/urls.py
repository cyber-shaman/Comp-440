from django.urls import path
from . import views

urlpatterns = [
 #   path('',views.get_Data),
    path('signup', views.signup),
    path('receiveData', views.receiveData),

    #path('test_token', views.test_token),
]