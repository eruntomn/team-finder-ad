from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from skills.models import Skill

from .forms import ProjectForm
from .models import Project

# Create your views here.


def project_list(request):
    projects = Project.objects.filter(status='open').order_by('-created_at')
    return render(
        request, 'projects/project_list.html', {'projects': projects}
    )


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(
        request, 'projects/project-details.html', {'project': project}
    )


@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Проверка: только владелец и статус open
    if request.user == project.owner and project.status == 'open':
        project.status = 'closed'
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})

    return JsonResponse(
        {'status': 'error', 'message': 'Недостаточно прав'}, status=403
    )


@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user in project.participants.all():
        project.participants.remove(request.user)
        is_participating = False
    else:
        project.participants.add(request.user)
        is_participating = True

    return JsonResponse(
        {
            'status': 'ok',
            'is_participating': is_participating,
            'participants_count': project.participants.count(),
        }
    )


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            # Добавляем автора в участники
            project.participants.add(request.user)
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()

    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': False},
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Проверка: только владелец может редактировать
    if project.owner != request.user:
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': True, 'project': project},
    )


@require_http_methods(['GET'])
def skills_autocomplete(request):
    """GET /projects/skills/?q=<текст> — возвращает навыки для автодополнения"""
    q = request.GET.get('q', '')
    skills = Skill.objects.filter(name__istartswith=q).order_by('name')[:10]
    data = [{'id': skill.id, 'name': skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_http_methods(['POST'])
def add_user_skill(request, project_id):
    """POST /projects/<project_id>/skills/add/ — добавляет навык текущему пользователю"""
    user = request.user

    import json

    data = json.loads(request.body)
    skill_id = data.get('skill_id')
    skill_name = data.get('name')

    added = False
    created = False

    if skill_id:
        try:
            skill = Skill.objects.get(id=skill_id)
        except Skill.DoesNotExist:
            return JsonResponse({'error': 'Навык не найден'}, status=404)
    elif skill_name:
        skill, created = Skill.objects.get_or_create(name=skill_name.strip())
    else:
        return JsonResponse(
            {'error': 'Не передан skill_id или name'}, status=400
        )

    if skill not in user.skills.all():
        user.skills.add(skill)
        added = True

    return JsonResponse(
        {
            'skill_id': skill.id,
            'name': skill.name,
            'created': created,
            'added': added,
        }
    )


@login_required
@require_http_methods(['POST'])
def remove_user_skill(request, project_id, skill_id):
    """POST /projects/<project_id>/skills/<skill_id>/remove/ — удаляет навык у текущего пользователя"""
    user = request.user

    try:
        skill = Skill.objects.get(id=skill_id)
    except Skill.DoesNotExist:
        return JsonResponse({'error': 'Навык не найден'}, status=404)

    if skill in user.skills.all():
        user.skills.remove(skill)
        return JsonResponse({'status': 'ok'})

    return JsonResponse(
        {'error': 'У пользователя нет такого навыка'}, status=400
    )
