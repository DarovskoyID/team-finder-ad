from os import name

from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from projectManager.forms import ProjectCreateForm
from projectManager.models import Project, Skill
from userManager.views import participants


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

    if request.user.is_authenticated:
        form = ProjectCreateForm(request.POST)
        user = request.user
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            github_url = form.cleaned_data['github_url']
            status = form.cleaned_data['status']

            your_project = Project.objects.create(name=name,
                                                  description=description,
                                                  owner=user,
                                                  github_url=github_url,
                                                  status=status)
            your_project.participants.add(user)

            return redirect('/projects/' + str(your_project.id))

        data = {'form': form}

        return render(request, "projects/create-project.html", data)

    return redirect('/users/login/')


def project_detail(request, project_id):

    project = Project.objects.get(id=project_id)
    data = {'project': project}

    return render(request, "projects/project-details.html", data)


def project_edit(request, project_id):
    if request.user.is_authenticated:
        project = Project.objects.get(id=project_id)
        if project.owner.email != request.user.email:
            return redirect('/projects/list/')
        form = ProjectCreateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            github_url = form.cleaned_data['github_url']
            status = form.cleaned_data['status']

            project.name = name
            project.description = description
            project.github_url = github_url
            project.status = status
            project.save()
            return redirect('/projects/'+str(project.id))

        data = {'form': form}

        return render(request, "projects/create-project.html", data)
    return redirect('/users/login/')