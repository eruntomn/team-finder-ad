from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('list/', views.user_list, name='user_list'),
    path('<int:user_id>/', views.user_profile, name='user_profile'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('skills/', views.skill_autocomplete, name='skill_autocomplete'),
    path('<int:user_id>/skills/add/', views.add_skill, name='add_skill'),
    path('<int:user_id>/skills/<int:skill_id>/remove/', views.remove_skill, name='remove_skill'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
]
