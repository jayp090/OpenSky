from django.urls import path
from . import views

urlpatterns = [
    # Your existing main page
    path('', views.Organisation_page, name='Organisation_Page'),
    
    # The new API endpoint for Cytoscape to fetch data
    path('api/teams-data/', views.team_data_api, name='team_data_api'),
    
    # Your existing detail page
    path('department/<int:dept_id>/', views.dept_detail, name='dept_detail'),
]