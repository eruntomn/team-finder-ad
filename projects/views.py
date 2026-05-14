from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from .forms import (
    CustomPasswordChangeForm,
    EditProfileForm,
    LoginForm,
    ProjectForm,
    RegisterForm,
)
from .models import Project, User


@require_GET
def root_redirect(request):
    return redirect('/projects/list/')


@require_GET
def project_list(request):
    projects = (
        Project.objects.select_related('owner')
        .prefetch_related('participants', 'interested_users')
        .order_by('-created_at')
    )
    paginator = Paginator(projects, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'projects/project_list.html',
        {
            'projects': projects,
            'page_obj': page_obj,
            'query_prefix': '',
        },
    )


@login_required
@require_GET
def favorite_projects(request):
    projects = (
        Project.objects.filter(interested_users=request.user)
        .select_related('owner')
        .prefetch_related('participants', 'interested_users')
        .order_by('-created_at')
    )
    return render(
        request,
        'projects/favorite.html',
        {
            'projects': projects,
        },
    )


@require_GET
def project_details(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related(
            'participants', 'interested_users'
        ),
        pk=project_id,
    )
    return render(
        request,
        'projects/project-details.html',
        {
            'project': project,
        },
    )


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.interested_users.filter(pk=request.user.pk).exists():
        project.interested_users.remove(request.user)
        favorited = False
    else:
        project.interested_users.add(request.user)
        favorited = True
    return JsonResponse(
        {
            'status': 'ok',
            'favorited': favorited,
        }
    )


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participating = False
    else:
        project.participants.add(request.user)
        participating = True
    return JsonResponse(
        {
            'status': 'ok',
            'participating': participating,
            'participants_count': project.participants.count(),
        }
    )


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse(
            {'status': 'error', 'message': 'Недостаточно прав'}, status=403
        )
    if project.status != 'open':
        return JsonResponse(
            {'status': 'error', 'message': 'Проект уже закрыт'}, status=400
        )
    project.status = 'closed'
    project.save(update_fields=['status'])
    return JsonResponse(
        {
            'status': 'ok',
            'project_status': 'closed',
        }
    )


@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect('/projects/list/')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/projects/list/')
    else:
        form = RegisterForm()
    return render(
        request,
        'users/register.html',
        {
            'form': form,
        },
    )


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/projects/list/')
    if request.method == 'POST':
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('/projects/list/')
    else:
        form = LoginForm(request=request)
    return render(
        request,
        'users/login.html',
        {
            'form': form,
        },
    )


@login_required
@require_GET
def logout_view(request):
    logout(request)
    return redirect('/projects/list/')


@require_GET
def users_list(request):
    participants = User.objects.all().order_by('id')
    active_filter = request.GET.get('filter')
    if request.user.is_authenticated and active_filter:
        if active_filter == 'owners-of-favorite-projects':
            participants = participants.filter(
                owned_projects__interested_users=request.user
            ).distinct()
        elif active_filter == 'owners-of-participating-projects':
            participants = participants.filter(
                owned_projects__participants=request.user
            ).distinct()
        elif active_filter == 'interested-in-my-projects':
            participants = participants.filter(
                favorite_projects__owner=request.user
            ).distinct()
        elif active_filter == 'participants-of-my-projects':
            participants = (
                participants.filter(participated_projects__owner=request.user)
                .exclude(pk=request.user.pk)
                .distinct()
            )
        else:
            active_filter = None
    paginator = Paginator(participants, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    query_prefix = ''
    if active_filter:
        query_prefix = f'filter={active_filter}&'
    return render(
        request,
        'users/participants.html',
        {
            'participants': participants,
            'page_obj': page_obj,
            'active_filter': active_filter,
            'query_prefix': query_prefix,
        },
    )


@require_GET
def user_details(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related('owned_projects__participants'),
        pk=user_id,
    )
    return render(
        request,
        'users/user-details.html',
        {
            'profile_user': profile_user,
        },
    )


@login_required
@require_http_methods(['GET', 'POST'])
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(
            request.POST, request.FILES, instance=request.user
        )
        if form.is_valid():
            form.save()
            return redirect(f'/users/{request.user.id}/')
    else:
        form = EditProfileForm(instance=request.user)
    return render(
        request,
        'users/edit_profile.html',
        {
            'form': form,
        },
    )


@login_required
@require_http_methods(['GET', 'POST'])
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f'/users/{request.user.id}/')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(
        request,
        'users/change_password.html',
        {
            'form': form,
        },
    )


@login_required
@require_http_methods(['GET', 'POST'])
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f'/projects/{project.id}/')
    else:
        form = ProjectForm()
    return render(
        request,
        'projects/create-project.html',
        {
            'form': form,
            'is_edit': False,
        },
    )


@login_required
@require_http_methods(['GET', 'POST'])
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return redirect(f'/projects/{project.id}/')
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            return redirect(f'/projects/{project.id}/')
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        'projects/create-project.html',
        {
            'form': form,
            'is_edit': True,
        },
    )
