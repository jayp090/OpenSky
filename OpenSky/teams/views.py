from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from .models import Team


@login_required
def team_list(request):
    query = request.GET.get('q', '')
    teams = Team.objects.all()

    if query:
        teams = teams.filter(
            Q(name__icontains=query) |
            Q(department__name__icontains=query) |
            Q(manager_name__icontains=query) |
            Q(skills__name__icontains=query)
        ).distinct()

    return render(request, 'teams/team_list.html', {
        'teams': teams,
        'query': query
    })


@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    return render(request, 'teams/team_detail.html', {
        'team': team
    })