from django.db import models

class TourStep(models.Model):
    order = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    page_name = models.CharField(max_length=100)
    section_id = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='tour_images', null=True, blank=True)
    video = models.FileField(upload_to='tour_videos', null=True, blank=True)

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