import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlencode
from django.views.decorators.http import require_POST

from projects.forms import ProjectCreateForm
from projects.models import Project, Skill
from team_finder.constants import NAME_MAX_LENGTH, SKILL_SEARCH_LIMIT
from team_finder.utils import paginate


def list_view(request):
    query = request.GET.get("skill", "").strip()

    active_skill = query
    projects = Project.objects.select_related(
        "owner"
    ).prefetch_related("skills", "participants")
    if query:
        skill = Skill.objects.filter(name=query).first()
        if skill:
            active_skill = skill.name
            projects = projects.filter(skills=skill)
        else:
            projects = projects.none()

    page_obj = paginate(request, projects)

    query = ""
    if active_skill:
        query = urlencode({"skill": active_skill}) + "&"

    data = {
        "page_obj": page_obj,
        "all_skills": Skill.objects.values_list(
            "name", flat=True
        ).distinct(),
        "active_skill": active_skill,
        "query_prefix": query,
        "projects": page_obj,
    }

    return render(request, "projects/project_list.html", data)


@login_required
def create_project(request):
    form = ProjectCreateForm(request.POST or None)
    if not form.is_valid():
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": False},
        )
    project = form.save(commit=False)
    project.owner = request.user
    project.save()
    project.participants.add(request.user)
    return redirect("projects:project_detail", project_id=project.pk)


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    data = {
        "project": project,
        "skill_name_max_length": NAME_MAX_LENGTH,
    }

    return render(request, "projects/project-details.html", data)


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return redirect("projects:list")
    form = ProjectCreateForm(request.POST or None, instance=project)
    if not form.is_valid():
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": True},
        )
    form.save()
    return redirect("projects:project_detail", project_id=project.pk)


def _owned_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        raise PermissionDenied
    return project


@require_POST
@login_required
def project_complete(request, project_id):
    project = _owned_project(request, project_id)
    if project.status != Project.Status.OPEN:
        return JsonResponse(
            {"error": "Проект уже закрыт."},
            status=HTTPStatus.BAD_REQUEST,
        )
    project.status = Project.Status.CLOSED
    project.save(update_fields=["status"])
    return JsonResponse(
        {
            "status": "ok",
            "project_status": project.status,
        }
    )


@require_POST
@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.status == Project.Status.CLOSED:
        return JsonResponse(
            {"error": "Проект уже закрыт."},
            status=HTTPStatus.BAD_REQUEST,
        )

    is_participant = not project.participants.filter(
        pk=request.user.pk
    ).exists()
    if is_participant:
        project.participants.add(request.user)
    else:
        project.participants.remove(request.user)
    return JsonResponse(
        {"status": "ok", "participant": is_participant}
    )


def skills_search(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse([], safe=False)

    skills = Skill.objects.filter(name__istartswith=query).values(
        "id", "name"
    )[:SKILL_SEARCH_LIMIT]

    return JsonResponse(list(skills), safe=False)


@require_POST
@login_required
def skill_add(request, project_id):
    project = _owned_project(request, project_id)
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Некорректный JSON."},
            status=HTTPStatus.BAD_REQUEST,
        )
    if not isinstance(data, dict) or (
        ("name" in data) == ("skill_id" in data)
    ):
        return JsonResponse(
            {"error": "Выберите один навык."},
            status=HTTPStatus.BAD_REQUEST,
        )
    created = False
    skill_name = data.get("name")
    skill_id = data.get("skill_id")
    if skill_name is not None:
        if not isinstance(skill_name, str):
            return JsonResponse(
                {"error": "Некорректное название навыка."},
                status=HTTPStatus.BAD_REQUEST,
            )
        skill_name = skill_name.strip()
        if not 1 <= len(skill_name) <= NAME_MAX_LENGTH:
            return JsonResponse(
                {"error": "Некорректное название навыка."},
                status=HTTPStatus.BAD_REQUEST,
            )
        skill, created = Skill.objects.get_or_create(name=skill_name)
    elif (
        isinstance(skill_id, (int, str))
        and not isinstance(skill_id, bool)
        and str(skill_id).isascii()
        and len(str(skill_id)) <= 10
        and str(skill_id).isdigit()
        and 0 < int(skill_id) <= 2147483647
    ):
        skill = get_object_or_404(Skill, pk=int(skill_id))
    else:
        return JsonResponse(
            {"error": "Некорректный навык."},
            status=HTTPStatus.BAD_REQUEST,
        )

    added = not project.skills.filter(pk=skill.pk).exists()
    project.skills.add(skill)

    return JsonResponse(
        {
            "skill_id": skill.pk,
            "name": skill.name,
            "created": created,
            "added": added,
        }
    )


@require_POST
@login_required
def skill_remove(request, project_id, skill_id):
    project = _owned_project(request, project_id)

    skill = get_object_or_404(project.skills, pk=skill_id)
    project.skills.remove(skill)

    return JsonResponse({"status": "ok"})
