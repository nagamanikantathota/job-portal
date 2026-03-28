from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.shortcuts import render

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='jobs/login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('company-profile/', views.company_profile_view, name='company_profile'),
    path('jobs/', views.job_list, name='job_list'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('application/<int:pk>/status/', views.update_application_status, name='update_application_status'),
    path('company/<int:pk>/', views.company_detail, name='company_detail'),
    path('job/<int:pk>/save/', views.toggle_save_job, name='toggle_save_job'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('seeker/dashboard/', views.seeker_dashboard, name='seeker_dashboard'),
    path('employer/post-job/', views.post_job, name='post_job'),
    path('employer/edit-job/<int:pk>/', views.edit_job, name='edit_job'),
    path('employer/delete-job/<int:pk>/', views.delete_job, name='delete_job'),
    path('admin-analytics/', views.admin_analytics, name='admin_analytics'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
]
