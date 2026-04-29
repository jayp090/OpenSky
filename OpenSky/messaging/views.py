from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models as db_models
from teams.models import TeamMember, Team
from .models import Message


# Create your views here.
def messaging_list(request):
    messaging = Message.objects.order_by('date') #uncomment when message added
    return render(request, 'accounts/message_list.html')
    
def messaging_detail(request, message_id):
    message    = get_object_or_404(Message, pk=message_id)
    return render(request, 'accounts/message_detail.html',{
        'message': message
        })

def messaging_create(request):
    teams = Team.objects.select_related('department') #not sure why departments is needed, but causes an error without selecting

    #put form code here
    if request.method == 'POST':
        sender       = request.POST.get('sender', '').strip()
        recipient    = request.POST.get('recipient')
        recipient_id = Team.objects.get(name=recipient)
        #for team in teams:
        #    if recipient == team.name:
        #        recipient_id = team
        subject    = request.POST.get('subject', '').strip()
        content  = request.POST.get('content', '').strip()
        
        Message.objects.create(sender=sender,recipient=recipient_id,subject=subject,content=content) #replace "sender" with request.user
        print("create() reached")
        
    
    
    return render(request, 'accounts/message_create.html', {
        'teams': teams
    })

