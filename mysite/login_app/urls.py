from django.conf.urls import url
from login_app import views
from django.urls import path

urlpatterns = [
    path('', views.login),
    path('logout', views.logout),
    path('home/', views.home),
    path('create_user/', views.create_user),
    path('update_user/', views.update_user),
    path('user_control/', views.User_Control().user_control),
    path('search_user_by_name/', views.User_Control().search_user_by_name),
    path('search_user_by_email/', views.User_Control().search_user_by_email),
    path('delete_user/', views.User_Control().delete_user),
    path('user_control_update/', views.User_Control().user_control_update),
    path('update/', views.User_Control().update)
]
