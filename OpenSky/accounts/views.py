from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def home(request):
    return HttpResponse("Home page")


def user_login(request):
    return HttpResponse("User login page")


def admin_login(request):
    return HttpResponse("Admin login page")


def signup(request):
    return HttpResponse("Signup page")


def dashboard(request):
    return HttpResponse("User dashboard")


def admin_dashboard(request):
    return HttpResponse("Admin dashboard")