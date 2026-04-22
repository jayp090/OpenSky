from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from teams.models import Team, Department, TeamMember

def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    return redirect('login')

@login_required
def dashboard(request):
    total_teams = Team.objects.count()
    total_depts = Department.objects.count()
    
    # Simple check for user's own teams (by email)
    user_email = request.user.email
    my_teams_count = TeamMember.objects.filter(email=user_email).values('team').distinct().count()
    
    context = {
        'total_teams': total_teams,
        'total_depts': total_depts,
        'my_teams_count': my_teams_count,
    }
    return render(request, 'core/dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    total_teams = Team.objects.count()
    total_depts = Department.objects.count()
    total_members = TeamMember.objects.count()
    
    context = {
        'total_teams': total_teams,
        'total_depts': total_depts,
        'total_members': total_members,
    }
    return render(request, 'core/admin_dashboard.html', context)