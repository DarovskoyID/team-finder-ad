import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlencode
from django.views.decorators.http import require_POST

from projectManager.forms import ProjectCreateForm
from projectManager.models import Project, Skill


def list_view(request):
    query = request.GET.get("skill", "").strip()

    active_skill = query
    projects = (
        Project.objects.select_related("owner")
        .prefetch_related("skills", "participants")
        .order_by("-created_at", "-pk")
    )
    if query:
        skill = Skill.objects.filter(name=query).first()
        if skill:
            active_skill = skill.name
            projects = projects.filter(skills=skill)
        else:
            projects = projects.none()

    paginator = Paginator(projects, 12)
    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    query = ""
    if active_skill:
        query = urlencode({"skill": active_skill}) + "&"

    data = {
        "page_obj": page_obj,
        "all_skills": Skill.objects.values_list("name", flat=True)
        .order_by("name")
        .distinct(),
        "active_skill": active_skill,
        "query_prefix": query,
        "projects": page_obj,
    }

    return render(request, "projects/project_list.html", data)


def _project_form(request, project=None):
    form = ProjectCreateForm(
        request.POST if request.method == "POST" else None,
        instance=project,
    )
    if request.method == "POST" and form.is_valid():
        saved_project = form.save(commit=False)
        if project is None:
            saved_project.owner = request.user
        saved_project.save()
        if project is None:
            saved_project.participants.add(request.user)
        return redirect(
            "projects:project_detail",
            project_id=saved_project.pk,
        )
    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": project is not None,
        },
    )


@login_required
def create_project(request):
    return _project_form(request)


def project_detail(request, project_id):

    project = get_object_or_404(Project, id=project_id)
    data = {"project": project}

    return render(request, "projects/project-details.html", data)


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.pk:
        return redirect("projects:list")
    return _project_form(request, project)


def _owned_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.pk:
        raise PermissionDenied
    return project


@require_POST
@login_required
def project_complete(request, project_id):
    project = _owned_project(request, project_id)
    if project.status != "open":
        return JsonResponse(
            {"error": "Проект уже закрыт."}, status=400
        )
    project.status = "closed"
    project.save(update_fields=["status"])
    return JsonResponse(
        {
            "status": "ok",
            "project_status": "closed",
        }
    )


@require_POST
@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.status == "closed":
        return JsonResponse({"status": "project closed"}, status=400)

    if not project.participants.filter(pk=request.user.pk).exists():
        project.participants.add(request.user)
        is_participant = True
    else:
        project.participants.remove(request.user)
        is_participant = False
    return JsonResponse(
        {"status": "ok", "participant": is_participant}
    )


def skills_search(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse([], safe=False)

    skills = (
        Skill.objects.filter(name__istartswith=query)
        .order_by("name")
        .values("id", "name")[:10]
    )

    return JsonResponse(list(skills), safe=False)


@require_POST
@login_required
def skill_add(request, project_id):
    project = _owned_project(request, project_id)
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Expected object"}, status=400)

    if ("name" in data) == ("skill_id" in data):
        return JsonResponse(
            {"error": "Выберите один навык."}, status=400
        )
    created = False
    skill_name = data.get("name")
    skill_id = data.get("skill_id")
    if skill_name is not None:
        if not isinstance(skill_name, str):
            return JsonResponse({"error": "Invalid name"}, status=400)
        skill_name = skill_name.strip()
        if not 1 <= len(skill_name) <= 124:
            return JsonResponse({"error": "Invalid name"}, status=400)
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
        return JsonResponse({"error": "Invalid skill"}, status=400)

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
