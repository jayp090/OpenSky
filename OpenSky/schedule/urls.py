from django.urls import path
from . import views

urlpatterns = [
    path('', views.schedule_view, name='schedule'),
    path('new/', views.create_meeting, name='create_meeting'),
]
