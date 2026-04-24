from django.db import models


class Department(models.Model):
    """Represents a Sky engineering department (e.g. Platform Engineering)."""
    name = models.CharField(max_length=100)
    head = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    """A technical skill tag that can be associated with multiple teams."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    """
    Central model representing a Sky engineering team.
    - department: FK to the owning department
    - skills: many-to-many tags describing what the team works with
    - upstream_dependencies: self-referential M2M — teams this team depends on.
      The reverse (downstream_teams) is automatically available on related teams.
    - github_url: optional link to the team's GitHub organisation or repo
    """
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams')
    manager_name = models.CharField(max_length=100)
    manager_email = models.EmailField()
    purpose = models.TextField()
    contact_channel = models.CharField(max_length=200, blank=True)
    github_url = models.URLField(blank=True, default='')
    skills = models.ManyToManyField(Skill, blank=True, related_name='teams')

    # Self-referential M2M: asymmetric so A depending on B does not imply B depends on A
    upstream_dependencies = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='downstream_teams'
    )

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """A person who belongs to a team. Identified by email for cross-referencing with User accounts."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f"{self.full_name} - {self.team.name}"


class AuditLog(models.Model):
    """
    Records every significant administrative action taken in the system.
    Written by the shared _log() helper function called from views.py files.
    Ordered most-recent-first so the admin dashboard always shows the latest activity.
    """
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    ACTION_CHOICES = [
        (ACTION_CREATE, 'Created'),
        (ACTION_UPDATE, 'Updated'),
        (ACTION_DELETE, 'Deleted'),
    ]
    action      = models.CharField(max_length=10, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=50)   # e.g. 'Team', 'Department', 'Member'
    object_name = models.CharField(max_length=200)  # human-readable name of the affected record
    performed_by = models.CharField(max_length=200) # username of the acting user
    timestamp   = models.DateTimeField(auto_now_add=True)
    details     = models.TextField(blank=True)      # optional extra context

    class Meta:
        ordering = ['-timestamp']  # newest first

    def __str__(self):
        return f"{self.action} {self.object_type}: {self.object_name}"


class MeetingRequest(models.Model):
    """
    A request submitted by a logged-in user to meet with a specific team.
    Date/time validation is enforced in the schedule_meeting view before saving.
    """
    team            = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='meetings')
    requester_name  = models.CharField(max_length=100)
    requester_email = models.EmailField()
    meeting_date    = models.DateField()
    meeting_time    = models.TimeField()
    platform        = models.CharField(max_length=100)  # e.g. 'Zoom', 'Microsoft Teams'
    message         = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meeting with {self.team.name} on {self.meeting_date}"

