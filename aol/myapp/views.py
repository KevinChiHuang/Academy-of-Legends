from django.shortcuts import render, HttpResponse
from .models import TodoItem
# Create your views here.
def home(request):
    return render(request, "home.html")

def board(request):
    return render(request, "board.html")