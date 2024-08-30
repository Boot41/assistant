from django.core.management.base import BaseCommand
from api.models import Company, CompanyInfo, Content

class Command(BaseCommand):
    help = 'Populate the database with Think41 information'

    def handle(self, *args, **options):
        self.stdout.write('Populating database with Think41 information...')

        # Create Think41 company
        think41, created = Company.objects.update_or_create(
            name="Think41",
            defaults={
                'description': "Think41 is a technology consulting company providing Custom Software as a Service (CSaaS).",
                'industry': "Technology Consulting",
                'founded_year': 2024,
                'website': "https://think41.com",
            }
        )
        self.stdout.write(f'{"Created" if created else "Updated"} company: {think41.name}')

        # Add company info
        company_info_data = [
            {'key': 'Career Email', 'value': 'career@think41.com', 'is_public': True},
            {'key': 'Funding', 'value': 'Self-funded with $2 million investment', 'is_public': True},
            {'key': 'Previous Company', 'value': 'HashedIn (acquired by Deloitte US in 2021)', 'is_public': True},
            {'key': 'Location', 'value': 'Bangalore, India', 'is_public': True},
            {'key': 'Service', 'value': 'Cloud-native app development', 'is_public': True},
            {'key': 'Service', 'value': 'Gen AI agent development', 'is_public': True},
            {'key': 'Service', 'value': 'LLM maintenance and operations', 'is_public': True},
            {'key': 'Technology', 'value': 'GenAI tools and frameworks', 'is_public': True},
            {'key': 'Technology', 'value': 'Cloud-native technologies', 'is_public': True},
            {'key': 'Client', 'value': 'Series B funded startups', 'is_public': True},
            {'key': 'Client', 'value': 'Mid-sized listed enterprises', 'is_public': True},
            {'key': 'Client', 'value': 'Deloitte', 'is_public': True},
            {'key': 'Founder', 'value': 'Anshuman Singh', 'is_public': True},
            {'key': 'Founder', 'value': 'Harshit Singhal', 'is_public': True},
            {'key': 'Founder', 'value': 'Himanshu Varshney', 'is_public': True},
            {'key': 'Founder', 'value': 'Sripathi Krishnan', 'is_public': True},
            {'key': 'Founder LinkedIn', 'value': 'https://www.linkedin.com/in/anshum4n/', 'is_public': True},
            {'key': 'Founder LinkedIn', 'value': 'https://www.linkedin.com/in/harshitsinghal01/', 'is_public': True},
            {'key': 'Founder LinkedIn', 'value': 'https://www.linkedin.com/in/himanshuhv/', 'is_public': True},
            {'key': 'Founder LinkedIn', 'value': 'https://www.linkedin.com/in/sripathikrishnan/', 'is_public': True},
        ]

        for info in company_info_data:
            obj, created = CompanyInfo.objects.update_or_create(
                company=think41,
                key=info['key'],
                defaults={'value': info['value'], 'is_public': info['is_public']}
            )
            self.stdout.write(f'{"Added" if created else "Updated"} company info: {info["key"]}')

        # Add content
        content_data = [
            {
                'content_type': 'text',
                'title': 'About Think41',
                'content': 'Think41 is a technology consulting company founded in 2024, providing Custom Software as a Service (CSaaS). We address the evolving needs of the software engineering industry, particularly with the advent of GenAI.'
            },
            {
                'content_type': 'text',
                'title': 'Our Approach',
                'content': 'We utilize GenAI tools and frameworks to deliver efficient and innovative software solutions. Our Autopod-based pricing model ensures transparency and flexibility for clients.'
            },
            {
                'content_type': 'text',
                'title': 'Our Founders',
                'content': 'Our founders have a strong background in cloud services and previously built HashedIn, acquired by Deloitte US in 2021. They bring expertise in technology, scalability, and management consulting.'
            },
            {
                'content_type': 'text',
                'title': 'Services',
                'content': 'We offer cloud-native app development, Gen AI agent development, and LLM maintenance and operations. All services are delivered through Autonomous Pods, cross-functional teams using Gen AI tools to enhance the software development lifecycle.'
            },
            {
                'content_type': 'text',
                'title': 'Technology Stack',
                'content': 'We employ various GenAI-focused technology tools and frameworks, including Agent Frameworks, customized chat interfaces, autonomous agents, vector stores, and embedding solutions.'
            }
        ]

        for content_item in content_data:
            obj, created = Content.objects.update_or_create(
                company=think41,
                title=content_item['title'],
                defaults={
                    'content_type': content_item['content_type'],
                    'content': content_item['content']
                }
            )
            self.stdout.write(f'{"Added" if created else "Updated"} content: {content_item["title"]}')

        self.stdout.write(self.style.SUCCESS('Think41 information added successfully'))