# Author: Jay Patel (w2105573)
import io
import json
import openpyxl
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from teams.models import Team, Department, TeamMember, AuditLog

User = get_user_model()
is_staff = lambda u: u.is_staff  # Reusable permission test for @user_passes_test


def home(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'dashboard')
    return redirect('login')


@login_required
def dashboard(request):
    total_teams = Team.objects.count()
    total_depts = Department.objects.count()
    total_deps  = Team.objects.filter(upstream_dependencies__isnull=False).count()

    user_email = request.user.email
    my_memberships = TeamMember.objects.filter(email=user_email).select_related('team__department')
    my_teams_count = my_memberships.values('team').distinct().count()

    from django.db.models import Count
    featured_teams = (
        Team.objects
        .select_related('department')
        .prefetch_related('skills')
        .annotate(member_count=Count('members'))
        .order_by('-member_count')[:6]
    )

    context = {
        'total_teams': total_teams,
        'total_depts': total_depts,
        'total_deps':  total_deps,
        'my_teams_count': my_teams_count,
        'my_memberships': my_memberships[:3],
        'featured_teams': featured_teams,
    }
    return render(request, 'core/dashboard.html', context)


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_dashboard(request):
    total_teams   = Team.objects.count()
    total_depts   = Department.objects.count()
    total_members = TeamMember.objects.count()
    total_users   = User.objects.count()
    total_admins  = User.objects.filter(is_staff=True).count()

    recent_teams = Team.objects.select_related('department').order_by('-id')[:5]
    audit_logs   = AuditLog.objects.all()[:10]  # Latest 10 actions for the audit panel

    # Build data arrays for the Chart.js bar charts on the admin dashboard.
    # Serialised to JSON here so the template can pass them directly to JS.
    depts_qs     = Department.objects.prefetch_related('teams').order_by('name')
    chart_labels  = json.dumps([d.name for d in depts_qs])
    chart_teams   = json.dumps([d.teams.count() for d in depts_qs])
    chart_members = json.dumps([
        TeamMember.objects.filter(team__department=d).count() for d in depts_qs
    ])

    context = {
        'total_teams':    total_teams,
        'total_depts':    total_depts,
        'total_members':  total_members,
        'total_users':    total_users,
        'total_admins':   total_admins,
        'recent_teams':   recent_teams,
        'audit_logs':     audit_logs,
        'chart_labels':   chart_labels,
        'chart_teams':    chart_teams,
        'chart_members':  chart_members,
    }
    return render(request, 'core/admin_dashboard.html', context)


# ── Reports ────────────────────────────────────────────────

@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_reports(request):
    return render(request, 'core/reports.html')


@user_passes_test(is_staff, login_url='/accounts/login/')
def report_teams_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Teams"

    headers = ['Team Name', 'Department', 'Manager', 'Manager Email',
               'Skills', 'Upstream Dependencies', 'Downstream Teams', 'Members']
    ws.append(headers)

    for team in Team.objects.select_related('department').prefetch_related(
            'skills', 'upstream_dependencies', 'downstream_teams', 'members'):
        ws.append([
            team.name,
            team.department.name if team.department else '',
            team.manager_name,
            team.manager_email,
            ', '.join(s.name for s in team.skills.all()),
            ', '.join(t.name for t in team.upstream_dependencies.all()),
            ', '.join(t.name for t in team.downstream_teams.all()),
            team.members.count(),
        ])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    resp = HttpResponse(buf.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = 'attachment; filename="opensky_teams.xlsx"'
    return resp


@user_passes_test(is_staff, login_url='/accounts/login/')
def report_departments_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Departments"

    ws.append(['Department', 'Head', 'Number of Teams', 'Teams'])

    for dept in Department.objects.prefetch_related('teams').all():
        ws.append([
            dept.name,
            dept.head,
            dept.teams.count(),
            ', '.join(t.name for t in dept.teams.all()),
        ])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    resp = HttpResponse(buf.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = 'attachment; filename="opensky_departments.xlsx"'
    return resp


@user_passes_test(is_staff, login_url='/accounts/login/')
def report_teams_print(request):
    """Print-friendly HTML for save-as-PDF."""
    teams = Team.objects.select_related('department').prefetch_related(
        'skills', 'upstream_dependencies', 'downstream_teams', 'members')
    return render(request, 'core/report_print.html', {'teams': teams, 'title': 'Full Team Report'})


@user_passes_test(is_staff, login_url='/accounts/login/')
def report_summary_print(request):
    depts = Department.objects.prefetch_related('teams').all()
    return render(request, 'core/report_summary_print.html', {'depts': depts, 'title': 'Department Summary'})
