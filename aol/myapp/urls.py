from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('admin/', views.admin, name='admin'),
    path('shop/', views.shop, name='shop'),
    path('board/', views.board, name='board'),
    path('add/', views.add, name='add'),
    path('settings/', views.settings, name='settings')
]

