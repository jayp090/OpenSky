from django.urls import path
from . import views

urlpatterns = [
    path('', views.org_overview, name='org_overview'),
    path('department/<int:dept_id>/', views.dept_detail, name='dept_detail'),
]
