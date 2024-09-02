from django.core.management.base import BaseCommand
from api.models import PPTSlide

class Command(BaseCommand):
    help = 'Populate PPT data'

    def handle(self, *args, **options):
        ppt_data = [
            {
                "title": "Welcome to Think41",
                "content": "Welcome to Think41's company pitch. We are a technology consulting firm with a product mindset, providing Custom Software on a Subscription (CSaaS). Our mission is to revolutionize the industry with our innovative solutions, leveraging GenAI to deliver custom-built software tailored to the exact needs of businesses.",
                "transcript": "Welcome to Think41's company pitch. We are a technology consulting firm with a product mindset, providing Custom Software on a Subscription (CSaaS). Our mission is to revolutionize the industry with our innovative solutions, leveraging GenAI to deliver custom-built software tailored to the exact needs of businesses.",
                "order": 1
            },
            {
                "title": "Consistent client-focused delivery lead to phenomenal growth",
                "content": "Slide-1: Consistent client-focused delivery lead to phenomenal growth\nOur founding team—Anshuman, Harshit, Himanshu, and Sripathi—have a proven track record of success. They founded HashedIn, scaling the company to 650 engineers before it was acquired by Deloitte. Following the acquisition, this same team didn't just maintain momentum; they quadrupled HashedIn’s size within three years and built a robust new AI division with 600 experts. With experience spanning both large enterprises and innovative startups, we're now leveraging AI and Gen-AI to develop faster, more impactful solutions, driving meaningful business results through cutting-edge software.",
                "transcript": "Slide-1: Consistent client-focused delivery lead to phenomenal growth\nOur founding team—Anshuman, Harshit, Himanshu, and Sripathi—have a proven track record of success. They founded HashedIn, scaling the company to 650 engineers before it was acquired by Deloitte. Following the acquisition, this same team didn't just maintain momentum; they quadrupled HashedIn’s size within three years and built a robust new AI division with 600 experts. With experience spanning both large enterprises and innovative startups, we're now leveraging AI and Gen-AI to develop faster, more impactful solutions, driving meaningful business results through cutting-edge software.",
                "order": 2
            },
            {
                "title": "Think41: Unlocking AI’s Potential with the 3Ps",
                "content": "Slide-2: Think41: Unlocking AI’s Potential with the 3Ps\nExperience the future of innovation with our comprehensive services that are designed to elevate your business. We boost productivity by automating workflows and introducing intelligent agents into processes like the SDLC. We pioneer transformative solutions by turning previously impossible use-cases into reality. And we expand possibilities by exploring and developing use-cases that push the boundaries of what’s imaginable. With us, your business doesn’t just keep pace with change—it leads it.",
                "transcript": "Slide-2: Think41: Unlocking AI’s Potential with the 3Ps\nExperience the future of innovation with our comprehensive services that are designed to elevate your business. We boost productivity by automating workflows and introducing intelligent agents into processes like the SDLC. We pioneer transformative solutions by turning previously impossible use-cases into reality. And we expand possibilities by exploring and developing use-cases that push the boundaries of what’s imaginable. With us, your business doesn’t just keep pace with change—it leads it.",
                "order": 3
            },
            # Add more slides as needed
        ]

        for slide in ppt_data:
            PPTSlide.objects.update_or_create(order=slide['order'], defaults=slide)

        self.stdout.write(self.style.SUCCESS('Successfully populated PPT data'))