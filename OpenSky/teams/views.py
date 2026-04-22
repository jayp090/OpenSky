from django.shortcuts import render


sample_teams = [
    {
        'id': 1,
        'name': 'Platform Engineering',
        'department': 'Engineering Operations',
        'manager': 'Jane Smith',
        'purpose': 'Supports internal engineering tools and deployment pipelines.',
        'skills': ['Python', 'Django', 'DevOps'],
        'upstream': ['Identity Team'],
        'downstream': ['Developer Experience Team'],
        'members': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
        'repositories': ['platform-api', 'deployment-portal'],
        'contact': 'platform@sky.uk'
    },
    {
        'id': 2,
        'name': 'Mobile Services',
        'department': 'Mobile Engineering',
        'manager': 'Michael Brown',
        'purpose': 'Builds and maintains backend services for mobile applications.',
        'skills': ['Java', 'Kotlin', 'APIs'],
        'upstream': ['Core API Team'],
        'downstream': ['iOS Team', 'Android Team'],
        'members': ['Tom', 'Jerry', 'Lina', 'Sara', 'Noah'],
        'repositories': ['mobile-gateway', 'auth-service'],
        'contact': 'mobile@sky.uk'
    }
]


def team_list(request):
    query = request.GET.get('q', '')
    teams = sample_teams

    if query:
        query_lower = query.lower()
        teams = [
            team for team in sample_teams
            if query_lower in team['name'].lower()
            or query_lower in team['department'].lower()
            or query_lower in team['manager'].lower()
        ]

    return render(request, 'teams/team_list.html', {
        'teams': teams,
        'query': query,
    })


def team_detail(request, team_id):
    team = next((team for team in sample_teams if team['id'] == team_id), None)
    return render(request, 'teams/team_detail.html', {'team': team})


def email_team(request, team_id):
    team = next((team for team in sample_teams if team['id'] == team_id), None)
    return render(request, 'teams/email_team.html', {'team': team})


def schedule_meeting(request, team_id):
    team = next((team for team in sample_teams if team['id'] == team_id), None)
    return render(request, 'teams/schedule_meeting.html', {'team': team})