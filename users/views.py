from http import HTTPStatus

from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from skills.models import Skill

from .forms import UserLoginForm, UserProfileForm, UserRegistrationForm
from .models import User


def user_list(request):
    all_skills = Skill.objects.all()
    active_skill = request.GET.get('skill', '')

    users = User.objects.order_by('id')

    if active_skill:
        users = users.filter(skills__name=active_skill)

    context = {
        'participants': users,
        'all_skills': all_skills,
        'active_skill': active_skill,
    }
    return render(request, 'users/participants.html', context)


def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    projects = user.owned_projects.all()
    return render(
        request,
        'users/user-details.html',
        {'user': user, 'projects': projects},
    )


@require_http_methods(['GET'])
def skill_autocomplete(request):
    q = request.GET.get('q', '')
    skills = Skill.objects.filter(name__istartswith=q).order_by('name')[:10]
    data = [{'id': skill.id, 'name': skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_http_methods(['POST'])
def add_skill(request, user_id):
    if request.user.id != user_id:
        return JsonResponse(
            {'error': 'Недостаточно прав'}, status=HTTPStatus.FORBIDDEN
        )

    user = request.user
    skill_id = request.POST.get('skill_id')
    skill_name = request.POST.get('name')

    added = False
    created = False

    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    elif skill_name:
        skill, created = Skill.objects.get_or_create(name=skill_name.strip())
    else:
        return JsonResponse(
            {'error': 'Не передан skill_id или name'},
            status=HTTPStatus.BAD_REQUEST,
        )

    if skill not in user.skills.all():
        user.skills.add(skill)
        added = True

    return JsonResponse(
        {'skill_id': skill.id, 'created': created, 'added': added}
    )


@login_required
@require_http_methods(['POST'])
def remove_skill(request, user_id, skill_id):
    if request.user.id != user_id:
        return JsonResponse(
            {'error': 'Недостаточно прав'}, status=HTTPStatus.FORBIDDEN
        )

    skill = get_object_or_404(Skill, id=skill_id)
    user = request.user

    if skill in user.skills.all():
        user.skills.remove(skill)
        return JsonResponse({'status': 'ok'})

    return JsonResponse(
        {'error': 'У пользователя нет такого навыка'},
        status=HTTPStatus.BAD_REQUEST,
    )


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST or None)
        if not form.is_valid():
            return render(request, 'users/register.html', {'form': form})

        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        auth_login(request, user)
        return redirect('users:login')

    form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST or None)
        if not form.is_valid():
            return render(request, 'users/login.html', {'form': form})

        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, email=email, password=password)

        if user is None:
            form.add_error(None, 'Неверный имейл или пароль')
            return render(request, 'users/login.html', {'form': form})

        auth_login(request, user)
        return redirect('projects:project_list')

    form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    auth_logout(request)
    return redirect('projects:project_list')


@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(
            request.POST or None, request.FILES or None, instance=user
        )
        if not form.is_valid():
            return render(request, 'users/edit_profile.html', {'form': form})

        form.save()
        return redirect('users:user_profile', user_id=user.id)

    form = UserProfileForm(instance=user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST or None)
        if not form.is_valid():
            return render(
                request, 'users/change_password.html', {'form': form}
            )

        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('users:user_profile', user_id=request.user.id)

    form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})
