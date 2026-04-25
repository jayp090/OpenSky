# Author: Jay Patel (w2105573)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models as db_models
from .models import Team, TeamMember, MeetingRequest, Department, Skill, AuditLog


# Writes a record to AuditLog; called after every admin create/update/delete
def _log(action, obj_type, obj_name, user, details=''):
    AuditLog.objects.create(
        action=action,
        object_type=obj_type,
        object_name=obj_name,
        performed_by=getattr(user, 'username', str(user)),
        details=details,
    )

# Used by @user_passes_test to restrict admin views to staff only
is_staff = lambda u: u.is_staff


# ── Public / Member views ──────────────────────────────────

def team_list(request):
    # Read filter/sort params from the query string
    query   = request.GET.get('q', '').strip()
    dept_id = request.GET.get('dept', '')
    sort    = request.GET.get('sort', 'name')

    teams = Team.objects.select_related('department').prefetch_related('skills', 'members')

    # Full-text search across name, department, and manager
    if query:
        teams = teams.filter(
            db_models.Q(name__icontains=query) |
            db_models.Q(department__name__icontains=query) |
            db_models.Q(manager_name__icontains=query)
        )

    if dept_id:
        teams = teams.filter(department_id=dept_id)

    # Dynamic ordering based on sort param
    if sort == 'department':
        teams = teams.order_by('department__name', 'name')
    elif sort == 'manager':
        teams = teams.order_by('manager_name')
    else:
        teams = teams.order_by('name')

    departments = Department.objects.all().order_by('name')

    return render(request, 'accounts/team_list.html', {
        'teams': teams,
        'query': query,
        'departments': departments,
        'selected_dept': dept_id,
        'sort': sort,
        'total': teams.count(),
    })


def team_detail(request, team_id):
    team    = get_object_or_404(Team, pk=team_id)
    members = TeamMember.objects.filter(team=team)
    upstream   = team.upstream_dependencies.all()
    downstream = team.downstream_teams.all()
    tab = request.GET.get('tab', 'overview')

    return render(request, 'accounts/team_detail.html', {
        'team': team,
        'members': members,
        'upstream': upstream,
        'downstream': downstream,
        'tab': tab,
    })


@login_required
def email_team(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if subject and message:
            messages.success(request, f'Your message to {team.name} has been sent!')
            return redirect('team_detail', team_id=team.id)
        else:
            messages.error(request, 'Subject and message are required.')
    return render(request, 'accounts/email_team.html', {'team': team})


@login_required
def schedule_meeting(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if request.method == 'POST':
        from datetime import date, datetime
        meeting_date = request.POST.get('meeting_date', '').strip()
        meeting_time = request.POST.get('meeting_time', '').strip()
        platform     = request.POST.get('platform', '').strip()
        message      = request.POST.get('message', '').strip()
        error = None

        if not meeting_date or not meeting_time or not platform:
            error = 'Date, time and platform are all required.'
        else:
            try:
                parsed_date = date.fromisoformat(meeting_date)
                # Server-side date validation — rejects past dates
                if parsed_date < date.today():
                    error = 'Meeting date cannot be in the past. Please choose a future date.'
                elif parsed_date == date.today():
                    # For today, also check the time hasn't already elapsed
                    if datetime.strptime(meeting_time, '%H:%M').time() <= datetime.now().time():
                        error = 'Meeting time has already passed for today. Please choose a later time.'
            except ValueError:
                error = 'Invalid date or time format.'

        if error:
            messages.error(request, error)
        else:
            MeetingRequest.objects.create(
                team=team,
                requester_name=request.user.get_full_name() or request.user.username,
                requester_email=request.user.email,
                meeting_date=meeting_date,
                meeting_time=meeting_time,
                platform=platform,
                message=message,
            )
            _log('create', 'Meeting Request', team.name, request.user,
                 f'Meeting on {meeting_date} at {meeting_time} via {platform}')
            messages.success(request, f'Meeting request with {team.name} submitted!')
            return redirect('team_detail', team_id=team.id)

    return render(request, 'accounts/schedule_meeting.html', {'team': team})


@login_required
def my_teams(request):
    user_email   = request.user.email
    memberships  = TeamMember.objects.filter(email=user_email).select_related('team__department')
    my_teams_qs  = Team.objects.filter(members__in=memberships).distinct()
    return render(request, 'accounts/my_teams.html', {'teams': my_teams_qs})


# ── Admin CRUD views ────────────────────────────────────────

@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_team_list(request):
    teams = Team.objects.select_related('department').prefetch_related('members').order_by('name')
    return render(request, 'teams/admin_team_list.html', {'teams': teams})


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_team_create(request):
    departments = Department.objects.all().order_by('name')
    if request.method == 'POST':
        name       = request.POST.get('name', '').strip()
        dept_id    = request.POST.get('department')
        manager    = request.POST.get('manager_name', '').strip()
        mgr_email  = request.POST.get('manager_email', '').strip()
        purpose    = request.POST.get('purpose', '').strip()
        channel    = request.POST.get('contact_channel', '').strip()
        skills_raw = request.POST.get('skills', '').strip()

        if not name:
            messages.error(request, 'Team name is required.')
        else:
            dept = None
            if dept_id:
                try:
                    dept = Department.objects.get(pk=dept_id)
                except Department.DoesNotExist:
                    pass

            github = request.POST.get('github_url', '').strip()
            team = Team.objects.create(
                name=name, department=dept,
                manager_name=manager, manager_email=mgr_email,
                purpose=purpose, contact_channel=channel,
                github_url=github,
            )

            for s in (s.strip() for s in skills_raw.split(',') if s.strip()):
                skill, _ = Skill.objects.get_or_create(name=s)
                team.skills.add(skill)

            _log('create', 'Team', name, request.user, f'Department: {dept}')
            messages.success(request, f'Team "{name}" created successfully.')
            return redirect('admin_team_list')

    return render(request, 'teams/admin_team_form.html', {
        'departments': departments, 'action': 'Create',
    })


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_team_edit(request, team_id):
    team        = get_object_or_404(Team, pk=team_id)
    departments = Department.objects.all().order_by('name')
    members     = TeamMember.objects.filter(team=team)

    if request.method == 'POST':
        team.name            = request.POST.get('name', team.name).strip()
        dept_id              = request.POST.get('department')
        team.manager_name    = request.POST.get('manager_name', team.manager_name).strip()
        team.manager_email   = request.POST.get('manager_email', team.manager_email).strip()
        team.purpose         = request.POST.get('purpose', team.purpose).strip()
        team.contact_channel = request.POST.get('contact_channel', team.contact_channel).strip()
        team.github_url      = request.POST.get('github_url', team.github_url).strip()
        skills_raw           = request.POST.get('skills', '').strip()

        if dept_id:
            try:
                team.department = Department.objects.get(pk=dept_id)
            except Department.DoesNotExist:
                pass

        team.save()

        team.skills.clear()
        for s in (s.strip() for s in skills_raw.split(',') if s.strip()):
            skill, _ = Skill.objects.get_or_create(name=s)
            team.skills.add(skill)

        _log('update', 'Team', team.name, request.user)
        messages.success(request, f'Team "{team.name}" updated.')
        return redirect('admin_team_list')

    skills_str = ', '.join(s.name for s in team.skills.all())
    return render(request, 'teams/admin_team_form.html', {
        'team': team, 'departments': departments,
        'members': members, 'skills_str': skills_str, 'action': 'Edit',
    })


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_team_delete(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if request.method == 'POST':
        name = team.name
        team.delete()
        _log('delete', 'Team', name, request.user)
        messages.success(request, f'Team "{name}" deleted.')
        return redirect('admin_team_list')
    return render(request, 'teams/admin_team_confirm_delete.html', {'team': team})


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_add_member(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        role      = request.POST.get('role', '').strip()
        email     = request.POST.get('email', '').strip()
        if full_name and role and email:
            if TeamMember.objects.filter(team=team, email=email).exists():
                messages.error(request, f'{email} is already a member of this team.')
            else:
                TeamMember.objects.create(team=team, full_name=full_name, role=role, email=email)
                _log('create', 'Member', full_name, request.user, f'Added to team: {team.name}')
                messages.success(request, f'{full_name} added to {team.name}.')
        else:
            messages.error(request, 'Name, role and email are required.')
    return redirect('admin_team_edit', team_id=team.id)


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_remove_member(request, member_id):
    member = get_object_or_404(TeamMember, pk=member_id)
    team_id = member.team_id
    if request.method == 'POST':
        name = member.full_name
        team_name = member.team.name
        member.delete()
        _log('delete', 'Member', name, request.user, f'Removed from team: {team_name}')
        messages.success(request, f'{name} removed.')
    return redirect('admin_team_edit', team_id=team_id)


# ── Department admin ───────────────────────────────────────

@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_dept_list(request):
    depts = Department.objects.prefetch_related('teams').order_by('name')
    return render(request, 'teams/admin_dept_list.html', {'depts': depts})


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_dept_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        head = request.POST.get('head', '').strip()
        desc = request.POST.get('description', '').strip()
        if not name:
            messages.error(request, 'Department name is required.')
        elif Department.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A department with this name already exists.')
        else:
            Department.objects.create(name=name, head=head, description=desc)
            _log('create', 'Department', name, request.user)
            messages.success(request, f'Department "{name}" created.')
            return redirect('admin_dept_list')
    return render(request, 'teams/admin_dept_form.html', {'action': 'Create'})


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_dept_edit(request, dept_id):
    dept = get_object_or_404(Department, pk=dept_id)
    if request.method == 'POST':
        dept.name        = request.POST.get('name', dept.name).strip()
        dept.head        = request.POST.get('head', dept.head).strip()
        dept.description = request.POST.get('description', dept.description).strip()
        dept.save()
        _log('update', 'Department', dept.name, request.user)
        messages.success(request, f'Department "{dept.name}" updated.')
        return redirect('admin_dept_list')
    return render(request, 'teams/admin_dept_form.html', {'dept': dept, 'action': 'Edit'})


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_dept_delete(request, dept_id):
    dept = get_object_or_404(Department, pk=dept_id)
    if request.method == 'POST':
        name = dept.name
        dept.delete()
        _log('delete', 'Department', name, request.user)
        messages.success(request, f'Department "{name}" deleted.')
        return redirect('admin_dept_list')
    return render(request, 'teams/admin_dept_confirm_delete.html', {'dept': dept})


# ── Dependency admin ───────────────────────────────────────

@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_team_dependencies(request, team_id):
    team      = get_object_or_404(Team, pk=team_id)
    all_teams = Team.objects.exclude(pk=team_id).order_by('name')

    if request.method == 'POST':
        action  = request.POST.get('action')
        dep_id  = request.POST.get('dep_team_id')
        try:
            dep_team = Team.objects.get(pk=dep_id)
        except Team.DoesNotExist:
            messages.error(request, 'Team not found.')
            return redirect('admin_team_dependencies', team_id=team_id)

        if action == 'add':
            team.upstream_dependencies.add(dep_team)
            _log('create', 'Dependency', team.name, request.user, f'Upstream: {dep_team.name} → {team.name}')
            messages.success(request, f'{dep_team.name} added as upstream dependency.')
        elif action == 'remove':
            team.upstream_dependencies.remove(dep_team)
            _log('delete', 'Dependency', team.name, request.user, f'Removed upstream: {dep_team.name} → {team.name}')
            messages.success(request, f'{dep_team.name} removed.')

        return redirect('admin_team_dependencies', team_id=team_id)

    return render(request, 'teams/admin_dependencies.html', {
        'team': team,
        'upstream': team.upstream_dependencies.all(),
        'downstream': team.downstream_teams.all(),
        'all_teams': all_teams,
    })
