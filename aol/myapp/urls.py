from django.urls import path
from.import views


urlpatterns = [

    path("", views.home, name="home"),
    path("board/", views.board, name="board"),
    path("shop/", views.shop, name="shop"),
    path("editStudents/", views.editStudents, name="editStudents")

]