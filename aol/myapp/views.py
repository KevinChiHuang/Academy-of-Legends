from django.shortcuts import render, HttpResponse
from .models import TodoItem
# Create your views here.
def home(request):
    return render(request, "home.html")

def board(request):
    return render(request, "board.html")

def shop(request):
    return render(request, "shop.html")

def editStudents(request):
    return render(request, "editStudents.html")