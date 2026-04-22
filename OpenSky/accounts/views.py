from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')

def user_login(request):
    return render(request, 'registration/user_login.html')

def admin_login(request):
    return render(request, 'registration/admin_login.html')

def signup(request):
    return render(request, 'registration/signup.html')

def dashboard(request):
    return render(request, 'core/dashboard.html')

def admin_dashboard(request):
    return render(request, 'core/admin_dashboard.html')