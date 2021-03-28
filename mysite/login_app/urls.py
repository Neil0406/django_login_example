from django.conf.urls import url
from login_app import views
from django.urls import path

urlpatterns = [
    path('', views.login),
    path('logout', views.logout),
    path('home/', views.home),
    path('create_user/', views.create_user),
     path('update_user/', views.update_user),

]
