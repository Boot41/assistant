from django.core.management.base import BaseCommand
from api.models import TourStep

class Command(BaseCommand):
    help = 'Populates or updates the database with tour steps'

    def handle(self, *args, **kwargs):
        tour_steps = [
            {
                'order': 1,
                'title': 'Welcome to the Tour',
                'description': 'This is the first step of our interactive tour. We will guide you through the main features of our application.',
                'page_name': 'Home',
                'content_type': 'video',
                'content': 'https://example.com/sample_video.mp4',
            },
            {
                'order': 2,
                'title': 'Exploring the Dashboard',
                'description': 'This is your dashboard. Here you can see an overview of your activities and quick access to main features.',
                'page_name': 'Dashboard',
                'content_type': 'image',
                'content': 'https://example.com/dashboard_image.jpg',
            },
            {
                'order': 3,
                'title': 'Creating a New Project',
                'description': 'Let\'s create a new project. Click on the "New Project" button to get started.',
                'page_name': 'Projects',
                'content_type': 'blog',
                'content': 'Here\'s a detailed guide on creating a new project...',
            },
            {
                'order': 4,
                'title': 'Customizing Your Profile',
                'description': 'You can customize your profile here. Add a profile picture and update your information.',
                'page_name': 'Profile',
                'content_type': 'image',
                'content': 'https://example.com/profile_customization.jpg',
            },
            {
                'order': 5,
                'title': 'Tour Completed',
                'description': 'Congratulations! You have completed the tour. Feel free to explore more on your own.',
                'page_name': 'Home',
                'content_type': 'video',
                'content': 'https://example.com/congratulations_video.mp4',
            },
        ]

        for step in tour_steps:
            TourStep.objects.update_or_create(
                order=step['order'],
                defaults=step
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated or updated tour steps'))