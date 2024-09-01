from django.core.management.base import BaseCommand
from api.models import UniversalContent

class Command(BaseCommand):
    help = 'Populate Think41 data into UniversalContent model'

    def handle(self, *args, **options):
        data = [
            {
                "title": "Think41 Basic Information",
                "content": "Think41 website is hosted at Think41.com. For career & referrals, email at career@think41.com.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Team and Background",
                "content": "Think41 is a technology consulting with product mindset providing Custom Software on a Subscription (CSaaS). Team previously built HashedIn, a cloud services & solutions company acquired by Deloitte US in 2021, now a cornerstone of Engineering Culture. The team has been in the technology services industry and were one of the leaders in the 'Born in Cloud' era through HashedIn, they have had the opportunity to cater to startups, unicorns, enterprises as well as large Fortune 500 companies.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Key Points",
                "content": "1) Proven Team: That built HashedIn, Born in Cloud services company, acquired by Deloitte. 2) Platform Shift: Re-imagining how software will be built in the post-Gen AI world. 3) Predictable Outcome: Build customised software for the existing organisational processes.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Problem Statement",
                "content": "Think41 is in the space of software engineering. The industry is going through rapid transformation due to GenAI. We believe that customised software development and management can be provided as a service or a subscription based model. We plan to bring in new models, both technology and commercial, to develop customised software, develop solutions and frameworks to bring this transformation.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Custom Software Services",
                "content": "We believe that given that each organisation is unique and with it's own business and decision making processes and metrics. Gen AI will enable us to build and deliver custom built software according to exact needs of the business, at the convenience of a product. With the efficiency of software development going up, we believe that increasingly more organisations would want customised software 'as a Service' in a subscription model.",
                "content_type": "services"
            },
            {
                "title": "Think41 Engagement Models",
                "content": "Yes. We do have a Autopod based pricing model in which we charge the customer. The basic cost of the cross-functional members working in the pod would be computed on a weekly basis for the billing.",
                "content_type": "services"
            },
            {
                "title": "Think41 Business Model Uniqueness",
                "content": "We believe that the subscription model can now be developed for the custom enterprise software. We, hence, would like to develop a 'Custom Software As a Service (CSaaS)'.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Technology Uniqueness",
                "content": "GenAI can significantly enhance productivity across the functional areas of software development. We have developed Autopods, a cross functional pod team which is enabled with custom and specialised automated agents to significantly enhance the speed, quality and productivity of software development.",
                "content_type": "technology"
            },
            {
                "title": "Think41 Autopods",
                "content": "Autopods are a cross-functional team of full stack engineers, engineering & product managers working alongside Gen AI agents to deliver end-to-end products & services. Autonomous Pods, or Autopods, extensively use Gen AI tools across the software development lifecycle to build faster.",
                "content_type": "services"
            },
            {
                "title": "Think41 Clients",
                "content": "Think41 team has worked extensively with unicorns, enterprises, global capability centres (GCCs) as well as large Fortune 500 companies both in India and the US. We are a fast growing and expanding.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Service Offerings",
                "content": "Our mission is to bring Gen AI to enterprises. We offer services across the stack and application of Gen AI: 1. Cloud Native App Development, 2. Gen AI - Agent Development, 3. LLM Maintenance & Ops. For all services, we engage as Autonomous Pods - a cross-functional team of full stack engineers, engineering & product managers working alongside Gen AI agents to deliver end-to-end products & services.",
                "content_type": "services"
            },
            {
                "title": "Think41 Funding",
                "content": "Think41 is a mid-sized start-up. It is self-funded by the founders who have had a successful exit to Deloitte. We are currently not looking for investments. However, if you are a strategic investor, it would be great if you could talk to one of the founders.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Founders Background",
                "content": "Think41 built HashedIn, a cloud services & solutions company acquired by Deloitte US in 2021, now a cornerstone of Engineering Culture. Before that, they worked at Trilogy, renowned in India for its 'Only The Best' (OTB) culture. They have a strong chemistry and long history of working together.",
                "content_type": "company_info"
            },
            {
                "title": "HashedIn Background",
                "content": "HashedIn was founded as a bootstrapped 'Born In Cloud' company in 2010 and known for its product development expertise, working with enterprises and unicorns clients. HashedIn was recognized as a Great Place to work and built several products, including one acquired by RedisLabs. Post-acquisition, we scaled HashedIn 4x to a team of 2500 in quick 3 years, proving the culture and engineering expertise.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 AI & Gen AI Expertise",
                "content": "Since early 2023, Think41 founders have built and scaled Gen AI capability at a Big 4 consulting firm, solving problems and innovating alongside Fortune500 clients. Before that, at HashedIn, they built a cloud engineering practice working with multiple enterprises & unicorns solving their AI and data challenges.",
                "content_type": "expertise"
            },
            {
                "title": "Think41 Founders",
                "content": "Think41 has four founders: Anshuman, Harshit, Himanshu & Sripathi.",
                "content_type": "company_info"
            },
            {
                "title": "Anshuman Singh (Anshu)",
                "content": "Anshu loves tech and scalability, having built hundreds of products and driven a CAGR growth of over 130% in the past 13 years. He approaches business problems like chess challenges, drawing from his expertise as a chess master. Outside of work, Anshu enjoys playing carrom and tennis, balancing his strategic mind with fun and competition. LinkedIn: https://www.linkedin.com/in/anshum4n/",
                "content_type": "founder_info"
            },
            {
                "title": "Harshit Singhal",
                "content": "Harshit loves business and has supercharged the growth trajectory for HashedIn, significantly expanding the mid-market segment for Deloitte. Previously, he co-founded Auctus Advisors, a strategy consulting firm acquired by YCP, and worked as a management consultant with SDG. Passionate about Indian history, Harshit also enjoys diving deep into the past to draw lessons for the future. LinkedIn: https://www.linkedin.com/in/harshitsinghal01/",
                "content_type": "founder_info"
            },
            {
                "title": "Himanshu Varshney",
                "content": "Himanshu is a people person. Along with leading HashedIn, he has championed the creation of an open culture at Deloitte Engineering and was recognized as one of India's Top 25 Trusted Leaders by GPTW. Formerly with Trilogy, Himanshu is also an All-Star sportsman from IIT Guwahati and HashedIn. He remains active in various sports, continually fostering teamwork and spirit. LinkedIn: https://www.linkedin.com/in/himanshuhv/",
                "content_type": "founder_info"
            },
            {
                "title": "Sripathi Krishnan (Sri)",
                "content": "Sri is a tech guy who served as the CTO and MD of Modern Software Engineering at Deloitte US, where he was responsible for technology strategy and GenAI innovation. He previously founded RDBTools, acquired by RedisLabs. Known as a champ for GenAI CoE, Sri is also a foodie who loves hosting and attending parties, blending his passion for technology with a zest for life. LinkedIn: https://www.linkedin.com/in/sripathikrishnan/",
                "content_type": "founder_info"
            },
            {
                "title": "Think41 Founders Location",
                "content": "The founders are based in Bangalore, India. They travel extensively to the Bay Area, US and are currently serving from India.",
                "content_type": "company_info"
            },
            # New one-liner facts
            {
                "title": "Think41 Website",
                "content": "Think41 website is hosted at Think41.com.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Career Contact",
                "content": "For career & referrals, email at career@think41.com.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Founders' LinkedIn Profiles",
                "content": "Profile of founder Anshuman Singh: https://www.linkedin.com/in/anshum4n/\nProfile of founder Harshit Singhal: https://www.linkedin.com/in/harshitsinghal01/\nProfile of founder Himanshu Varshney: https://www.linkedin.com/in/himanshuhv/\nProfile of founder Sripathi Krishnan: https://www.linkedin.com/in/sripathikrishnan/",
                "content_type": "founder_info"
            },
            {
                "title": "Think41 Founders' HashedIn Background",
                "content": "Think41 founders previously founded and were Managing Directors at HashedIn after its acquisition by Deloitte https://hashedin.com/",
                "content_type": "company_info"
            },
            {
                "title": "HashedIn Acquisition",
                "content": "HashedIn is a cloud services & solutions company acquired by Deloitte US in 2021.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Experience",
                "content": "Think41 has years of experience catering to startups, unicorns, enterprises, and large Fortune 500 companies.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Funding Status",
                "content": "Think41 is self-funded by the founders.",
                "content_type": "company_info"
            },
            {
                "title": "Think41 Founders' Previous Work",
                "content": "Think41 founders earlier worked at Trilogy Inc., known for its 'Only The Best' culture.",
                "content_type": "company_info"
            },
            {
                "title": "Anshuman Singh Interests",
                "content": "Think41 Founder Anshuman Singh has driven significant product growth and enjoys chess, carom, and tennis.",
                "content_type": "founder_info"
            },
            {
                "title": "Harshit Singhal Interests",
                "content": "Think41 Founder Harshit Singhal has expanded mid-market segments and is passionate about Indian history.",
                "content_type": "founder_info"
            },
            {
                "title": "Himanshu Varshney Interests",
                "content": "Think41 Founder Himanshu Varshney fosters open culture and teamwork, being an active sportsman.",
                "content_type": "founder_info"
            },
            {
                "title": "Sripathi Krishnan Interests",
                "content": "Think41 Founder Sripathi Krishnan blends technology expertise with a love for hosting and attending parties.",
                "content_type": "founder_info"
            },
        ]

        for item in data:
            UniversalContent.objects.create(**item)

        self.stdout.write(self.style.SUCCESS('Successfully populated Think41 data'))