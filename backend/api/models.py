from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone

def get_default_company():
    from .models import Company
    return Company.objects.get_or_create(name=settings.DEFAULT_COMPANY_NAME)[0]

class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    industry = models.CharField(max_length=100)
    founded_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1800), MaxValueValidator(2100)],
        null=True,  # Add this line
        blank=True  # Add this line
    )
    website = models.URLField()
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['industry']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CompanyInfo(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='info')
    key = models.CharField(max_length=100)
    value = models.TextField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'key')
        indexes = [
            models.Index(fields=['company', 'key']),
            models.Index(fields=['is_public']),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.key}"

class TourStep(models.Model):
    CONTENT_TYPES = (
        ('video', 'Video'),
        ('image', 'Image'),
        ('blog', 'Blog'),
        ('interactive', 'Interactive'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tour_steps', default=get_default_company)
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    page_name = models.CharField(max_length=100)
    section_id = models.CharField(max_length=100, blank=True, null=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='blog')
    content = models.TextField(default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'order')
        indexes = [
            models.Index(fields=['company', 'order']),
            models.Index(fields=['content_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.order}. {self.title}"

    next_step = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_step')

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.next_step:
            next_step = TourStep.objects.filter(company=self.company, order__gt=self.order).order_by('order').first()
            if next_step and next_step != self:
                self.next_step = next_step
                self.save()

class Content(models.Model):
    CONTENT_TYPES = (
        ('video', 'Video'),
        ('image', 'Image'),
        ('text', 'Text'),
        ('interactive', 'Interactive'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contents', null=True, blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['company', 'content_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.company.name if self.company else 'No Company'} - {self.get_content_type_display()}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.company:
            self.company = Company.objects.get_or_create(name=settings.DEFAULT_COMPANY_NAME)[0]
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    preferred_content_type = models.CharField(max_length=20, choices=Content.CONTENT_TYPES, default='text')
    interests = models.JSONField(default=list)
    points = models.PositiveIntegerField(default=0)
    current_tour_step = models.ForeignKey(TourStep, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'company']),
            models.Index(fields=['preferred_content_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.company.name if self.company else 'No Company'}"

class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, default=get_default_company)
    tour_step = models.ForeignKey(TourStep, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "User Histories"
        indexes = [
            models.Index(fields=['user', 'company']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.company.name if self.company else 'No Company'} - {self.tour_step.title}"

    def save(self, *args, **kwargs):
        if not self.company:
            self.company = get_default_company()
        super().save(*args, **kwargs)