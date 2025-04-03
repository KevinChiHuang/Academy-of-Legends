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
    path('students/', views.student_list, name='student_list'),
    
    # Edit student routes
    path('edit-student/<str:student_id>/', views.edit_student, name='edit_student'),
    path('update-student/<str:student_id>/', views.update_student_details, name='update_student_details'),
    
    # AJAX endpoints
    path('update_student/', views.update_student, name='update_student'),
    path('delete_student/', views.delete_student, name='delete_student'),
    
    # Other routes
    path('upload/', views.upload_image, name='upload_image'),
    path('get_image/<str:image_id>/', views.get_image, name="get_image"),
    path('buy/<str:reward_id>/', views.buy_reward, name='buy_reward'),
    path('remove-reward/<str:reward_id>/', views.remove_reward, name='remove_reward'),
    path('delete-item/<str:student_id>/<str:item_id>/', views.delete_item, name='delete_item'),
]