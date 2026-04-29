from django.db import models
from teams.models import TeamMember, Team

# Create your models here.
    
class Message(models.Model):

    sender = models.CharField(max_length=100) #expecting user
    recipient =  models.ForeignKey(Team, on_delete=models.CASCADE, related_name='messages')
    subject = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateField(auto_now=True) #automatically set date when message.create() is called

    def __str__(self):
        return self.subject