from django.urls import path
from . import views

urlpatterns = [
    # ── Member-facing routes ───────────────────────────────────────────────
    path('', views.team_list, name='team_list'),
    path('my-teams/', views.my_teams, name='my_teams'),
    path('<int:team_id>/', views.team_detail, name='team_detail'),
    path('<int:team_id>/email/', views.email_team, name='email_team'),
    path('<int:team_id>/schedule/', views.schedule_meeting, name='schedule_meeting'),

    # Admin – teams
    path('admin/teams/', views.admin_team_list, name='admin_team_list'),
    path('admin/teams/create/', views.admin_team_create, name='admin_team_create'),
    path('admin/teams/<int:team_id>/edit/', views.admin_team_edit, name='admin_team_edit'),
    path('admin/teams/<int:team_id>/delete/', views.admin_team_delete, name='admin_team_delete'),
    path('admin/teams/<int:team_id>/members/add/', views.admin_add_member, name='admin_add_member'),
    path('admin/members/<int:member_id>/remove/', views.admin_remove_member, name='admin_remove_member'),
    path('admin/teams/<int:team_id>/dependencies/', views.admin_team_dependencies, name='admin_team_dependencies'),

    # Admin – departments
    path('admin/departments/', views.admin_dept_list, name='admin_dept_list'),
    path('admin/departments/create/', views.admin_dept_create, name='admin_dept_create'),
    path('admin/departments/<int:dept_id>/edit/', views.admin_dept_edit, name='admin_dept_edit'),
    path('admin/departments/<int:dept_id>/delete/', views.admin_dept_delete, name='admin_dept_delete'),
]
