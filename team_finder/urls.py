from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from projects.views import project_list, project_detail, complete_project, toggle_participate, create_project, edit_project
from projects.views import skills_autocomplete, add_user_skill, remove_user_skill
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='project_list', permanent=False)),
    path('projects/list/', project_list, name='project_list'),
    path('projects/<int:project_id>/', project_detail, name='project_detail'),
    path('projects/<int:project_id>/complete/',
         complete_project, name='complete_project'),
    path('projects/<int:project_id>/toggle-participate/',
         toggle_participate, name='toggle_participate'),
    path('projects/create-project/', create_project, name='create_project'),
    path('projects/<int:project_id>/edit/', edit_project, name='edit_project'),
    path('users/', include('users.urls')),
    path('projects/skills/', skills_autocomplete, name='skills_autocomplete'),
    path('projects/<int:project_id>/skills/add/',
         add_user_skill, name='add_user_skill'),
    path('projects/<int:project_id>/skills/<int:skill_id>/remove/',
         remove_user_skill, name='remove_user_skill'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
