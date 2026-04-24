from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('reports/', views.admin_reports, name='admin_reports'),
    path('reports/teams/excel/', views.report_teams_excel, name='report_teams_excel'),
    path('reports/departments/excel/', views.report_departments_excel, name='report_departments_excel'),
    path('reports/teams/print/', views.report_teams_print, name='report_teams_print'),
    path('reports/summary/print/', views.report_summary_print, name='report_summary_print'),
]
