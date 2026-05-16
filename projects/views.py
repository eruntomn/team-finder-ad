from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProjectForm
from .models import Project


def project_list(request):
    projects = (
        Project.objects.filter(status=Project.STATUS_OPEN)
        .select_related('owner')
        .prefetch_related('participants')
    )
    return render(
        request, 'projects/project_list.html', {'projects': projects}
    )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related(
            'participants'
        ),
        id=project_id,
    )
    return render(
        request, 'projects/project-details.html', {'project': project}
    )


@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user == project.owner and project.status == Project.STATUS_OPEN:
        project.status = Project.STATUS_CLOSED
        project.save()
        return JsonResponse(
            {'status': 'ok', 'project_status': Project.STATUS_CLOSED}
        )

    return JsonResponse(
        {'status': 'error', 'message': 'Недостаточно прав'},
        status=HTTPStatus.FORBIDDEN,
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
    if request.method != 'POST':
        form = ProjectForm()
        return render(
            request,
            'projects/create-project.html',
            {'form': form, 'is_edit': False},
        )

    form = ProjectForm(request.POST or None)
    if not form.is_valid():
        return render(
            request,
            'projects/create-project.html',
            {'form': form, 'is_edit': False},
        )

    project = form.save(commit=False)
    project.owner = request.user
    project.save()
    project.participants.add(request.user)
    return redirect('project_detail', project_id=project.id)


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return redirect('project_detail', project_id=project.id)

    if request.method != 'POST':
        form = ProjectForm(instance=project)
        return render(
            request,
            'projects/create-project.html',
            {'form': form, 'is_edit': True, 'project': project},
        )

    form = ProjectForm(request.POST or None, instance=project)
    if not form.is_valid():
        return render(
            request,
            'projects/create-project.html',
            {'form': form, 'is_edit': True, 'project': project},
        )

    form.save()
    return redirect('project_detail', project_id=project.id)
