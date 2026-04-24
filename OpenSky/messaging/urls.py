from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='messaging_inbox'),
    path('compose/', views.compose, name='messaging_compose'),
    path('<int:pk>/', views.message_detail, name='message_detail'),
    path('<int:pk>/delete/', views.delete_message, name='delete_message'),
]
