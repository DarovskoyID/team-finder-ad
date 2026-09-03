from django.core.paginator import Paginator
from django.shortcuts import render

from projectManager.models import Project, Skill


def list(request):

    projects = Project.objects.all().order_by('-created_at')

    active_skill = request.GET.get('active_skill')
    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    query = ''
    if active_skill:
        query = f'skill={active_skill}&'


    data = {
        'page_obj' : page_obj,
        'all_skills' : Skill.objects.values_list('name', flat=True).distinct(),
        'active_skill' : active_skill,
        'query_prefix': query
    }

    return render(request, 'projects/project_list.html', data)


def create_project(request):
    return render(request, "projects/create-project.html")