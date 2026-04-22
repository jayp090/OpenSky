from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Team, TeamMember, MeetingRequest


def team_list(request):
    """List all teams with optional search."""
    query = request.GET.get('q', '')
    teams = Team.objects.all()

    if query:
        query_lower = query.lower()
        teams = teams.filter(
            models.Q(name__icontains=query_lower) |
            models.Q(department__name__icontains=query_lower) |
            models.Q(manager_name__icontains=query_lower)
        )

    return render(request, 'accounts/team_list.html', {
        'teams': teams,
        'query': query,
    })


def team_detail(request, team_id):
    """Show details of a specific team."""
    team = get_object_or_404(Team, pk=team_id)
    members = TeamMember.objects.filter(team=team)

    return render(request, 'accounts/team_detail.html', {
        'team': team,
        'members': members,
    })


@login_required
def email_team(request, team_id):
    """Email a team - creates a message record."""
    team = get_object_or_404(Team, pk=team_id)

    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')

        if subject and message:
            # In a real app, you would send an email here
            # For now, just show success message
            messages.success(request, f'Your message to {team.name} has been sent!')
            return redirect('team_detail', team_id=team.id)

    return render(request, 'accounts/email_team.html', {'team': team})


@login_required
def schedule_meeting(request, team_id):
    """Schedule a meeting with a team."""
    team = get_object_or_404(Team, pk=team_id)

    if request.method == 'POST':
        meeting_date = request.POST.get('meeting_date', '')
        meeting_time = request.POST.get('meeting_time', '')
        platform = request.POST.get('platform', '')
        message = request.POST.get('message', '')

        if meeting_date and meeting_time and platform:
            MeetingRequest.objects.create(
                team=team,
                requester_name=request.user.username,
                requester_email=request.user.email,
                meeting_date=meeting_date,
                meeting_time=meeting_time,
                platform=platform,
                message=message
            )
            messages.success(request, f'Meeting request with {team.name} has been submitted!')
            return redirect('team_detail', team_id=team.id)

    return render(request, 'accounts/schedule_meeting.html', {'team': team})


@login_required
def my_teams(request):
    """Show teams that the current user belongs to."""
    # Get team members for the current user (by email match)
    user_email = request.user.email
    my_memberships = TeamMember.objects.filter(email=user_email)
    my_teams = Team.objects.filter(members__in=my_memberships).distinct()

    return render(request, 'accounts/my_teams.html', {
        'teams': my_teams,
    })
