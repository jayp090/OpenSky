from django.db import models

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=100)
    head = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams')
    manager_name = models.CharField(max_length=100)
    manager_email = models.EmailField()
    purpose = models.TextField()
    contact_channel = models.CharField(max_length=200, blank=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name='teams')
    upstream_dependencies = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='downstream_teams'
    )

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f"{self.full_name} - {self.team.name}"


class MeetingRequest(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='meetings')
    requester_name = models.CharField(max_length=100)
    requester_email = models.EmailField()
    meeting_date = models.DateField()
    meeting_time = models.TimeField()
    platform = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meeting with {self.team.name} on {self.meeting_date}"

