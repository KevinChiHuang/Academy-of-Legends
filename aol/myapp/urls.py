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
    path('settings/', views.settings, name='settings'),
    path('students/', views.student_list, name='student_list'),  # Fix: Use views.student_list
    path('update_student/', views.update_student, name='update_student'),  # Fix: Use views.update_student
    path('delete_student/', views.delete_student, name='delete_student'),  # Fix: Use views.delete_student
]

