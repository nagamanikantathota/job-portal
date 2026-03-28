from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

def default_expiry():
    return timezone.now() + timedelta(days=30)

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=50, blank=True, help_text="FontAwesome class, e.g., fa-laptop-code")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Company(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    description = models.TextField()
    website = models.URLField(max_length=200, blank=True)
    location = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

class Profile(models.Model):
    USER_TYPES = (
        ('seeker', 'Job Seeker'),
        ('employer', 'Employer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    bio = models.TextField(blank=True)
    experience = models.CharField(max_length=100, blank=True)
    skills = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    preferred_category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Remote', 'Remote'),
        ('Freelance', 'Freelance'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    )
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs_posted')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs', null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='jobs')
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='Full-time')
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(default=default_expiry)

    def __str__(self):
        return f"{self.title} at {self.company.name if self.company else 'N/A'}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expiry_date

class Application(models.Model):
    STATUS_CHOICES = (
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview', 'Interview'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications_made')
    resume = models.FileField(upload_to='applications/')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'seeker') # Prevent duplicate applications

    def __str__(self):
        return f"{self.seeker.username} applied for {self.job.title} - {self.status}"

class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, user_type='seeker')

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()