import openpyxl
import re
from django.core.management.base import BaseCommand
from teams.models import Team, Department, Skill

class Command(BaseCommand):
    help = 'Import teams from Excel registry'

    def handle(self, *args, **kwargs):
        path = r'C:\Users\Admin\Desktop\New folder\OneDrive - University of Westminster\Level 5\SEM-4\CW - Software Development Group Project\materials\Agile Project Module UofW - Team Registry.xlsx'
        
        try:
            wb = openpyxl.load_workbook(path)
            sheet = wb.active
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error opening workbook: {e}"))
            return

        # Clear existing data to avoid duplicates during development
        Team.objects.all().delete()
        Department.objects.all().delete()
        Skill.objects.all().delete()

        rows = list(sheet.iter_rows(min_row=2, values_only=True))
        
        for row in rows:
            if not row[3]:  # Team Name
                continue

            dept_name = row[0] or "General"
            dept_head = row[2] or ""
            team_leader = row[1] or "Unknown"
            team_name = row[3]
            purpose = row[8] or ""
            skills_raw = row[9] or ""
            slack = row[15] or ""

            # Get or create department
            department, _ = Department.objects.get_or_create(
                name=dept_name,
                defaults={'head': dept_head}
            )

            # Create Team
            team = Team.objects.create(
                name=team_name,
                department=department,
                manager_name=team_leader,
                manager_email=f"{team_leader.lower().replace(' ', '.')}@sky.uk", # Placeholder email
                purpose=purpose,
                contact_channel=slack
            )

            # Handle Skills
            if skills_raw:
                # Split by commas, newlines, or semicolons
                skill_names = re.split(r'[,;\n]+', str(skills_raw))
                for s_name in skill_names:
                    s_name = s_name.strip()
                    if s_name:
                        skill, _ = Skill.objects.get_or_create(name=s_name)
                        team.skills.add(skill)

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {len(rows)} teams."))
