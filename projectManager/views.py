import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlencode
from django.views.decorators.http import require_POST

from projectManager.forms import ProjectCreateForm
from projectManager.models import Project, Skill


def list_view(request):
    query = request.GET.get('skill', '').strip()

    active_skill = ''

    if query:
        skill = Skill.objects.filter(name=query).first()
        if skill:
            active_skill = skill.name
            projects = Project.objects.all().filter(
                skills=skill.id).order_by('-created_at')
        else:
            projects = Project.objects.none()
    else:
        projects = Project.objects.all().order_by('-created_at')

    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    query = ''
    if active_skill:
        query = urlencode({'skill': active_skill}) + '&'

    data = {
        'page_obj': page_obj,
        'all_skills': Skill.objects.values_list('name', flat=True).order_by('name').distinct(),
        'active_skill': active_skill,
        'query_prefix': query,
        'projects': True,
    }

    return render(request, 'projects/project_list.html', data)


def create_project(request):

    if request.user.is_authenticated:
        if request.method == "POST":
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
        else:
            form = ProjectCreateForm()

        data = {'form': form}

        return render(request, "projects/create-project.html", data)

    return redirect('/users/login/')


def project_detail(request, project_id):

    project = get_object_or_404(Project, id=project_id)
    data = {'project': project}

    return render(request, "projects/project-details.html", data)


def project_edit(request, project_id):
    if request.user.is_authenticated:
        project = get_object_or_404(Project, id=project_id)

        if project.owner.id != request.user.id:
            return redirect('/projects/list/')

        if request.method == "POST":
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
        elif request.method == "GET":
            form = ProjectCreateForm(initial={
                'name': project.name,
                'description': project.description,
                'github_url': project.github_url,
                'status': project.status
            })
        data = {
            'form': form,
            'is_edit': True,
        }

        return render(request, "projects/create-project.html", data)
    return redirect('/users/login/')


@require_POST
@login_required
def project_complete(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user.id == project.owner.id:
        project.status = "closed"
        project.save()
    else:
        return JsonResponse({'error': 'You are not have permission to complete this project.'}, status=403)
    return JsonResponse({'status': 'ok'})


@require_POST
@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.status == "closed":
        return JsonResponse({'status': 'project closed'}, status=400)

    if request.user not in project.participants.all():
        project.participants.add(request.user)
        project.save()
        is_participant = True
    else:
        project.participants.remove(request.user)
        project.save()
        is_participant = False
    return JsonResponse({'status': 'ok', 'participant': is_participant})


def skills_search(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'skills': []})

    skills = Skill.objects.filter(
        name__icontains=query).values('id', 'name')[:10]

    return JsonResponse(list(skills), safe=False)


@require_POST
@login_required
def skill_add(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return JsonResponse({'error': 'You are not have permission'}, status=403)

    try:
        data = json.loads(request.body)
        skill_name = data.get('name')
        skill_id = data.get('skill_id')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if skill_name and len(skill_name) <= 128:
        skill, _ = Skill.objects.get_or_create(name=skill_name)
    elif skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    else:
        return JsonResponse({'error': 'Empty name'}, status=400)

    project.skills.add(skill)

    return JsonResponse({'status': 'ok', 'id': skill.id, 'name': skill.name})


@require_POST
@login_required
def skill_remove(request, project_id, skill_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return JsonResponse({'error': 'You are not have permission'}, status=403)

    project.skills.remove(skill_id)

    return JsonResponse({'status': 'ok'})
