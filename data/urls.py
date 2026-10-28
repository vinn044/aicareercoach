from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import TemplateView
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/logged-out/', TemplateView.as_view(template_name='accounts/logout.html'), name='logged_out'),
    path('accounts/profile/', views.profile, name='profile'),
    path('resumes/', views.resume_list, name='resume_list'),
    path('resumes/new/', views.resume_create, name='resume_create'),
    path('resumes/<int:pk>/', views.resume_detail, name='resume_detail'),
    path('resumes/<int:pk>/edit/', views.resume_edit, name='resume_edit'),
    path('resumes/<int:pk>/delete/', views.resume_delete, name='resume_delete'),
    path('feedback/<int:pk>/status/', views.feedback_status, name='feedback_status'),
    path('matches/', views.job_matches, name='job_matches'),
]
