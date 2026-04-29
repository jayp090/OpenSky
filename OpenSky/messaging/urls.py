from django.urls import path
from . import views
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models as db_models
urlpatterns = [
    path('', views.messaging_list, name='messaging_list'),
    path('create/', views.messaging_create, name='messaging_create'),
    path('<int:message_id>/', views.messaging_detail, name='messaging_detail'),
    #path('<int:message_id>/delete/', views.delete_message, name='delete_message'), #not needed
]
