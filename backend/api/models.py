from django.db import models
from django.contrib.auth.models import User

class TourStep(models.Model):
    CONTENT_TYPES = (
        ('video', 'Video'),
        ('image', 'Image'),
        ('blog', 'Blog'),
    )
    order = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    page_name = models.CharField(max_length=100)
    section_id = models.CharField(max_length=100, blank=True, null=True)
    content_type = models.CharField(max_length=5, choices=CONTENT_TYPES, default='blog')
    content = models.TextField(default='')

    def __str__(self):
        return f"{self.order}. {self.title}"

class Content(models.Model):
    CONTENT_TYPES = (
        ('video', 'Video'),
        ('image', 'Image'),
        ('text', 'Text'),
    )
    content_type = models.CharField(max_length=5, choices=CONTENT_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    def __str__(self):
        return f"{self.get_content_type_display()}: {self.title}"

class UserProgress(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    current_step = models.ForeignKey(TourStep, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"User {self.user_id} - Step {self.current_step.order if self.current_step else 'N/A'}"

class Quiz(models.Model):
    tour_step = models.ForeignKey(TourStep, on_delete=models.CASCADE, related_name='quizzes')
    question = models.TextField()
    options = models.JSONField()
    correct_answer = models.CharField(max_length=200)

    def __str__(self):
        return f"Quiz for {self.tour_step.title}"

class UserPoints(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"User {self.user_id} - Points: {self.points}"

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_content_type = models.CharField(max_length=20, choices=[
        ('video', 'Video'),
        ('image', 'Image'),
        ('text', 'Text'),
        ('interactive', 'Interactive')
    ])
    interests = models.JSONField(default=list)

class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour_step = models.ForeignKey(TourStep, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)