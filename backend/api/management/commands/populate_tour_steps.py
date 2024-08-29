from django.core.management.base import BaseCommand
from api.models import TourStep, Company
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populates or updates the database with tour steps'

    def handle(self, *args, **kwargs):
        # Ensure a default company exists
        company, _ = Company.objects.get_or_create(
            name="Default Company",
            defaults={
                'slug': 'default-company',
                'description': 'This is a default company for tour steps.',
                'industry': 'Technology',
                'founded_year': timezone.now().year,  # Use current year as default
                'website': 'https://example.com',
                'active': True
            }
        )

        tour_steps = [
            {
                'order': 1,
                'title': 'Welcome to Our Website',
                'description': 'Welcome to our interactive tour! We\'ll guide you through the main features of our website.',
                'page_name': 'LandingPage',
                'content_type': 'text',
                'content': 'This is our landing page. Here you can find an overview of our services and latest insights.',
                'section_id': 'hero-section'
            },
            {
                'order': 2,
                'title': 'Exploring Our Services',
                'description': 'Let\'s take a look at our services section.',
                'page_name': 'LandingPage',
                'content_type': 'text',
                'content': 'Our services include AI solutions, data analytics, and more. Click on each service to learn more.',
                'section_id': 'services-section'
            },
            {
                'order': 3,
                'title': 'Latest Insights',
                'description': 'Stay up-to-date with our latest insights and blog posts.',
                'page_name': 'LandingPage',
                'content_type': 'text',
                'content': 'Here you can find our most recent articles and insights about AI and technology trends.',
                'section_id': 'latest-insights-section'
            },
            {
                'order': 4,
                'title': 'About Us',
                'description': 'Learn more about our company and mission.',
                'page_name': 'AboutUs',
                'content_type': 'text',
                'content': 'Our About Us page provides information about our company history, values, and team.',
                'section_id': 'about-us-main'
            },
            {
                'order': 5,
                'title': 'Visualizing AI',
                'description': 'Explore our AI visualization tools and demos.',
                'page_name': 'Visualizingai',
                'content_type': 'text',
                'content': 'This page showcases our AI visualization capabilities. Interact with the demos to see AI in action.',
                'section_id': 'ai-visualization-demo'
            },
            {
                'order': 6,
                'title': 'Career Opportunities',
                'description': 'Discover career opportunities at our company.',
                'page_name': 'CareersPage',
                'content_type': 'text',
                'content': 'Browse our current job openings and learn about the benefits of working with us.',
                'section_id': 'job-listings'
            },
            {
                'order': 7,
                'title': 'Contact Us',
                'description': 'Get in touch with us for any inquiries.',
                'page_name': 'Footer',
                'content_type': 'text',
                'content': 'You can find our contact information in the footer. Feel free to reach out with any questions!',
                'section_id': 'contact-info'
            },
        ]

        for step in tour_steps:
            TourStep.objects.update_or_create(
                company=company,
                order=step['order'],
                defaults={**step, 'company': company}
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated or updated tour steps'))