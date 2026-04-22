from django.shortcuts import render


def team_list(request):
    return render(request, 'teams/team_list.html')


def team_detail(request, team_id):
    return render(request, 'teams/team_detail.html', {'team_id': team_id})