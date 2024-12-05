from django.urls import re_path
from . import views

urlpatterns = [
    re_path('login', views.login),
    re_path('logout', views.logout),
    re_path('signup', views.signup),
    re_path('whoami', views.get_current_user),
    re_path('test_token', views.test_token),
]
