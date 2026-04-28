from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from teams.models import Team, Department, Skill
from django.contrib.auth.decorators import login_required

@login_required
def Organisation_page(request):
    return render(request, 'organization/chart.html')


def dept_detail(request, dept_id):
    # Fetch the specific department or return 404
    dept = get_object_or_404(Department, id=dept_id)
    
    # Fetch all teams belonging to this department to list them on the page
    teams = dept.teams.all() 
    
    return render(request, 'organization/chart.html', {
        'dept': dept,
        'teams': teams
    })



def team_data_api(request):
    # Sort Departments alphabetically by name
    departments = Department.objects.all().order_by('name')
    
    # Prefetch teams, sorting them by name as well for consistent layout
    teams = Team.objects.select_related('department').prefetch_related(
        'upstream_dependencies', 
        'skills'
    ).all().order_by('name')
    
    elements = []

    # 1. Add Department "Parent" Nodes
    for dept in departments:
        elements.append({
            'data': {
                'id': f'dept_{dept.id}', 
                'label': dept.name,
                'type': 'department',
                'head': dept.head
            }
        })

    # 2. Add Team Nodes
    for team in teams:
        skill_list = [skill.name for skill in team.skills.all()]
        
        elements.append({
            'data': {
                'id': str(team.id), 
                'label': team.name,
                # Crucial: Ties the team to the sorted Department
                'parent': f'dept_{team.department_id}', 
                'manager': team.manager_name,
                'purpose': team.purpose,
                'skills': skill_list,
                'github': team.github_url
            }
        })

        # 3. Add Dependency Edges, does upstream as it should fill out recursively and not need to be both ways hopefully?
        for upstream in team.upstream_dependencies.all():
            elements.append({
                'data': {
                    'id': f'edge_{upstream.id}_{team.id}',
                    'source': str(upstream.id), 
                    'target': str(team.id)
                }
            })

    return JsonResponse(elements, safe=False)





