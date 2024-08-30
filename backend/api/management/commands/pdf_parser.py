import os
import PyPDF2
from django.core.management.base import BaseCommand
from api.models import Company, CompanyInfo

class Command(BaseCommand):
    help = 'Parse PDF and populate database with company information'

    def add_arguments(self, parser):
        parser.add_argument('pdf_path', type=str, help='Path to the PDF file')

    def handle(self, *args, **options):
        pdf_path = os.path.abspath(options['pdf_path'])
        self.stdout.write(f'Attempting to open PDF file: {pdf_path}')
        
        if not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f'PDF file not found: {pdf_path}'))
            return

        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()

        # Parse the content
        lines = text.split('\n')
        company_name = "Think41"
        company_description = "Think41 is a technology consulting with product mindset providing Custom Software on a Subscription (CSaaS)."
        
        company_data = {
            'name': company_name,
            'description': company_description,
            'industry': 'Technology Consulting',
            'founded_year': None,  # We don't have this information in the provided text
            'website': 'Think41.com',
        }

        company, created = Company.objects.update_or_create(
            name=company_name,
            defaults=company_data
        )

        # Parse and store additional information
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                CompanyInfo.objects.update_or_create(
                    company=company,
                    key=key.strip(),
                    defaults={'value': value.strip()}
                )

        # Store founder information
        founders = [
            ("Anshuman Singh", "https://www.linkedin.com/in/anshum4n/"),
            ("Harshit Singhal", "https://www.linkedin.com/in/harshitsinghal01/"),
            ("Himanshu Varshney", "https://www.linkedin.com/in/himanshuhv/"),
            ("Sripathi Krishnan", "https://www.linkedin.com/in/sripathikrishnan/")
        ]

        for founder_name, linkedin_url in founders:
            CompanyInfo.objects.update_or_create(
                company=company,
                key=f"Founder: {founder_name}",
                defaults={'value': linkedin_url}
            )

        # Store other important information
        important_info = [
            ("Email", "career@think41.com"),
            ("Funding", "Self-funded by the founders"),
            ("Previous Company", "HashedIn, acquired by Deloitte US in 2021"),
            ("Location", "Bangalore, India"),
        ]

        for key, value in important_info:
            CompanyInfo.objects.update_or_create(
                company=company,
                key=key,
                defaults={'value': value}
            )

        # Store service offerings
        service_offerings = [
            "Cloud Native App Development",
            "Gen AI - Agent Development",
            "LLM Maintenance & Ops"
        ]

        for service in service_offerings:
            CompanyInfo.objects.update_or_create(
                company=company,
                key="Service Offering",
                defaults={'value': service}
            )

        # Store GenAI tools and frameworks
        genai_tools = {
            "Agent Frameworks": ["Crewai", "Langchain", "AutogenAI"],
            "Chat User Interface": ["OpenWebUI", "Nextchat", "Librechat"],
            "Autonomous Agents": ["Autogpt", "Play", "Agentgpt"],
            "Vector Stores": ["Milvus", "Chroma", "MongoDB"],
            "Embedding": ["OpenAI", "Huggingface sentence transformers", "Facebook AI research Embedding"],
            "LLM adoption": ["OpenAI", "Anthropic", "Cohere", "Llama 3", "Mistral", "Hugging Face", "OpenRouter", "Groq"],
            "LLM Fine Tuning": ["Snorkel.ai", "Labelbox", "Appen"],
            "Image, Audio & Video": ["Midjourney", "Synthesia", "Amazon Transcribe", "Suno"]
        }

        for category, tools in genai_tools.items():
            CompanyInfo.objects.update_or_create(
                company=company,
                key=f"GenAI Tools - {category}",
                defaults={'value': ', '.join(tools)}
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully parsed PDF and updated database for {company_name}'))
