from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from .models import Job, Application, Profile, Category, SavedJob, Company
from .forms import RegistrationForm, JobForm, ApplicationForm, ProfileForm, UserUpdateForm, CompanyForm, ContactForm

def get_profile_completion(user):
    try:
        profile = user.profile
        points = 0
        total = 5
        if user.first_name and user.last_name: points += 1
        if user.email: points += 1
        if profile.resume: points += 1
        if profile.skills: points += 1
        if profile.experience: points += 1
        return int((points / total) * 100)
    except Exception:
        return 0

def home(request):
    # Only show non-expired featured jobs
    featured_jobs = Job.objects.filter(is_featured=True, expiry_date__gt=timezone.now()).order_by('-created_at')[:6]
    categories = Category.objects.annotate(job_count=Count('jobs', filter=Q(jobs__expiry_date__gt=timezone.now())))
    return render(request, 'jobs/home.html', {
        'featured_jobs': featured_jobs,
        'categories': categories
    })

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            if user.profile.user_type == 'employer':
                return redirect('company_profile')
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'jobs/register.html', {'form': form})

def job_list(request):
    # Base queryset: only non-expired jobs with related data optimized
    jobs_list = Job.objects.filter(expiry_date__gt=timezone.now()).select_related('company', 'category').order_by('-created_at')
    categories = Category.objects.all()

    # Advanced Search Filters
    q = request.GET.get('q')
    location = request.GET.get('location')
    company_name = request.GET.get('company')
    category_id = request.GET.get('category')
    date_posted = request.GET.get('date_posted')
    job_type = request.GET.get('job_type')
    min_salary = request.GET.get('min_salary')

    if q:
        jobs_list = jobs_list.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(requirements__icontains=q))
    if location:
        jobs_list = jobs_list.filter(location__icontains=location)
    if company_name:
        jobs_list = jobs_list.filter(company__name__icontains=company_name)
    if category_id:
        jobs_list = jobs_list.filter(category_id=category_id)
    if job_type:
        jobs_list = jobs_list.filter(job_type=job_type)
    if min_salary:
        try:
            jobs_list = jobs_list.filter(Q(salary_max__gte=min_salary) | Q(salary_min__gte=min_salary))
        except ValueError:
            pass
    
    if date_posted:
        now = timezone.now()
        if date_posted == 'today':
            jobs_list = jobs_list.filter(created_at__gte=now - datetime.timedelta(days=1))
        elif date_posted == 'week':
            jobs_list = jobs_list.filter(created_at__gte=now - datetime.timedelta(days=7))
        elif date_posted == 'month':
            jobs_list = jobs_list.filter(created_at__gte=now - datetime.timedelta(days=30))

    paginator = Paginator(jobs_list, 10)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'categories': categories,
        'job_types': Job.JOB_TYPE_CHOICES,
        'query': q,
        'location': location,
        'company_name': company_name,
        'category_id': category_id,
        'date_posted': date_posted,
        'job_type_selected': job_type,
        'min_salary': min_salary
    })

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()
    return render(request, 'jobs/job_detail.html', {'job': job, 'is_saved': is_saved})

def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    # Only show active jobs from this company
    jobs = company.jobs.filter(expiry_date__gt=timezone.now()).order_by('-created_at')
    return render(request, 'jobs/company_detail.html', {'company': company, 'jobs': jobs})

@login_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    # Check if expired
    if job.is_expired:
        messages.error(request, 'This job has expired.')
        return redirect('job_list')

    if request.user.profile.user_type != 'seeker':
        messages.error(request, 'Only job seekers can apply for jobs.')
        return redirect('home')
    
    # Check for duplicate
    if Application.objects.filter(job=job, seeker=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('seeker_dashboard')
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.seeker = request.user
            application.save()
            
            # Email Notification to Applicant
            try:
                subject = f"Application Confirmation: {job.title}"
                message = f"Hi {request.user.username},\n\nYou have successfully applied for the position of {job.title} at {job.company.name}."
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])
            except Exception as e:
                print(f"DEBUG Email Error: {e}")

            messages.success(request, f'Successfully applied for {job.title}!')
            return redirect('seeker_dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})

@login_required
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if application.job.employer != request.user and not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()
            
            # Email Notification to Seeker
            try:
                subject = f"Application Update: {application.job.title}"
                message = f"Hi {application.seeker.username},\n\nYour application status for '{application.job.title}' has been updated to: {new_status}."
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [application.seeker.email])
            except Exception as e:
                print(f"DEBUG Email Error: {e}")
                
            messages.success(request, f"Status updated to {new_status} and seeker notified.")
    
    return redirect('employer_dashboard')

@login_required
def toggle_save_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created:
        saved_job.delete()
        messages.info(request, f'"{job.title}" removed from saved jobs.')
    else:
        messages.success(request, f'"{job.title}" saved successfully.')
    return redirect('job_detail', pk=pk)

@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'jobs/profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })

@login_required
def company_profile_view(request):
    if request.user.profile.user_type != 'employer':
        return redirect('home')
    company, created = Company.objects.get_or_create(employer=request.user)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company profile updated successfully!')
            return redirect('employer_dashboard')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'jobs/company_profile.html', {'form': form})

@login_required
def employer_dashboard(request):
    if request.user.profile.user_type != 'employer':
        return redirect('home')
    if not hasattr(request.user, 'company'):
        return redirect('company_profile')
    jobs = request.user.jobs_posted.annotate(applicant_count=Count('applications')).order_by('-created_at')
    return render(request, 'jobs/employer_dashboard.html', {'jobs': jobs, 'status_choices': Application.STATUS_CHOICES})

@login_required
def seeker_dashboard(request):
    if request.user.profile.user_type != 'seeker':
        return redirect('home')
    
    applications = request.user.applications_made.all().order_by('-applied_at')
    saved_jobs = request.user.saved_jobs.all().order_by('-saved_at')
    
    # Profile Completion
    completion_percentage = get_profile_completion(request.user)
    
    # Recommendation System
    user_skills = request.user.profile.skills.split(',') if request.user.profile.skills else []
    pref_cat = request.user.profile.preferred_category
    
    # Only recommend non-expired jobs
    recommendations = Job.objects.filter(expiry_date__gt=timezone.now()).exclude(applications__seeker=request.user)
    
    if pref_cat:
        recommendations = recommendations.filter(category=pref_cat)[:5]
    elif user_skills:
        skill_queries = Q()
        for skill in user_skills:
            skill_queries |= Q(title__icontains=skill.strip()) | Q(description__icontains=skill.strip())
        recommendations = recommendations.filter(skill_queries).distinct()[:5]
    else:
        recommendations = recommendations.filter(is_featured=True)[:5]

    return render(request, 'jobs/seeker_dashboard.html', {
        'applications': applications,
        'saved_jobs': saved_jobs,
        'recommendations': recommendations,
        'completion_percentage': completion_percentage
    })

@user_passes_test(lambda u: u.is_superuser)
def admin_analytics(request):
    total_users = User.objects.count()
    total_jobs = Job.objects.count()
    total_applications = Application.objects.count()
    total_seekers = Profile.objects.filter(user_type='seeker').count()
    total_employers = Profile.objects.filter(user_type='employer').count()
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    recent_apps = Application.objects.order_by('-applied_at')[:5]
    return render(request, 'jobs/admin_analytics.html', {
        'total_users': total_users,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'total_seekers': total_seekers,
        'total_employers': total_employers,
        'recent_jobs': recent_jobs,
        'recent_apps': recent_apps
    })

@login_required
def post_job(request):
    if request.user.profile.user_type != 'employer':
        return redirect('home')
    if not hasattr(request.user, 'company'):
        return redirect('company_profile')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.company = request.user.company
            job.save()
            messages.success(request, 'Job vacancy posted successfully!')
            return redirect('employer_dashboard')
    else:
        form = JobForm()
    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('employer_dashboard')
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/post_job.html', {'form': form, 'edit': True})

@login_required
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('employer_dashboard')
    return render(request, 'jobs/delete_job.html', {'job': job})

def about(request):
    return render(request, 'jobs/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, "Your message has been sent. We will get back to you soon!")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'jobs/contact.html', {'form': form})

def faq(request):
    return render(request, 'jobs/faq.html')

def user_logout(request):
    logout(request)
    return redirect('home')
