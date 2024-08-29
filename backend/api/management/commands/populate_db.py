from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Company, CompanyInfo, TourStep, Content, UserProfile
from django.conf import settings

class Command(BaseCommand):
    help = 'Populate the database with company information'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating database with company information...')

        # Company details
        name = input("Enter company name: ")
        description = input("Enter company description: ")
        industry = input("Enter company industry: ")
        founded_year = int(input("Enter founding year: "))
        website = input("Enter company website: ")

        company, created = Company.objects.get_or_create(
            name=name,
            defaults={
                'description': description,
                'industry': industry,
                'founded_year': founded_year,
                'website': website,
            }
        )
        self.stdout.write(f'{"Created" if created else "Updated"} company: {company.name}')

        # Company info
        while True:
            key = input("Enter company info key (or press enter to finish): ")
            if not key:
                break
            value = input(f"Enter value for {key}: ")
            is_public = input(f"Is {key} public? (y/n): ").lower() == 'y'
            CompanyInfo.objects.update_or_create(
                company=company, key=key,
                defaults={'value': value, 'is_public': is_public}
            )

        # Tour steps
        step_order = 1
        while True:
            title = input(f"Enter title for tour step {step_order} (or press enter to finish): ")
            if not title:
                break
            description = input("Enter step description: ")
            page_name = input("Enter page name for this step: ")
            content = input("Enter step content: ")
            TourStep.objects.update_or_create(
                company=company, order=step_order,
                defaults={
                    'title': title,
                    'description': description,
                    'page_name': page_name,
                    'content': content,
                }
            )
            step_order += 1

        # Content
        while True:
            content_type = input("Enter content type (video/image/text/interactive) or press enter to finish: ")
            if not content_type:
                break
            title = input("Enter content title: ")
            content = input("Enter content (URL for video/image, text for others): ")
            Content.objects.create(
                company=company,
                content_type=content_type,
                title=title,
                content=content
            )

        self.stdout.write(self.style.SUCCESS('Company information added successfully'))