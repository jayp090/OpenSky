# Author: Jay Patel (w2105573)
from django.contrib import admin

# Register your models here.
from .models import Department, Skill, Team, TeamMember, MeetingRequest

admin.site.register(Department)
admin.site.register(Skill)
admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(MeetingRequest)