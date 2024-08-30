from django.core.management.base import BaseCommand
from api.models import Company, TourStep

class Command(BaseCommand):
    help = 'Populate the database with tour steps'

    def handle(self, *args, **options):
        company, created = Company.objects.get_or_create(name="Think41")
        
        tour_steps = [
            {
                "title": "Welcome to Our Website",
                "description": "Welcome to our interactive tour! We'll guide you through the main features of our website.",
                "content": "This is our landing page. Here you can find an overview of our services and latest insights.",
                "page_name": "home"
            },
            {
                "title": "Exploring Our Services",
                "description": "Let's take a look at our services section.",
                "content": "Our services include AI solutions, data analytics, and more. Click on each service to learn more.",
                "page_name": "services"
            },
            {
                "title": "Latest Insights",
                "description": "Stay up-to-date with our latest insights and blog posts.",
                "content": "Here you can find our most recent articles and insights about AI and technology trends.",
                "page_name": "insights"
            },
            {
                "title": "About Us",
                "description": "Learn more about our company and mission.",
                "content": "Our About Us page provides information about our company history, values, and team.",
                "page_name": "about"
            },
            {
                "title": "Visualizing AI",
                "description": "Explore our AI visualization tools and demos.",
                "content": "This page showcases our AI visualization capabilities. Interact with the demos to see AI in action.",
                "page_name": "ai-demo"
            },
            {
                "title": "Career Opportunities",
                "description": "Discover career opportunities at our company.",
                "content": "Browse our current job openings and learn about the benefits of working with us.",
                "page_name": "careers"
            },
            {
                "title": "Contact Us",
                "description": "Get in touch with us for any inquiries.",
                "content": "You can find our contact information in the footer. Feel free to reach out with any questions!",
                "page_name": "contact"
            }
        ]

        for index, step in enumerate(tour_steps):
            TourStep.objects.update_or_create(
                company=company,
                order=index,
                defaults={
                    "title": step["title"],
                    "description": step["description"],
                    "content": step["content"],
                    "page_name": step["page_name"]
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated tour steps'))