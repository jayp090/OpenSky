from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request, 'core/admin_dashboard.html')