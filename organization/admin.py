from django.contrib import admin

# Register your models here.
from .models import Department, Skill, Team, TeamMember, MeetingRequest


admin.site.register(MeetingRequest)
admin.site.register(TeamMember)
admin.site.register(Department)
admin.site.register(Team)