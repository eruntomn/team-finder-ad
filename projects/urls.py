from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('list/', views.project_list, name='project_list'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path(
        '<int:project_id>/complete/',
        views.complete_project,
        name='complete_project',
    ),
    path(
        '<int:project_id>/toggle-participate/',
        views.toggle_participate,
        name='toggle_participate',
    ),
    path('create-project/', views.create_project, name='create_project'),
    path('<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('skills/', views.skills_autocomplete, name='skills_autocomplete'),
    path(
        '<int:project_id>/skills/add/',
        views.add_user_skill,
        name='add_user_skill',
    ),
    path(
        '<int:project_id>/skills/<int:skill_id>/remove/',
        views.remove_user_skill,
        name='remove_user_skill',
    ),
]
