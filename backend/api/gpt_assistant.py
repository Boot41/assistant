import os
import json
import logging
import requests
from dotenv import load_dotenv
from .models import Company, CompanyInfo, Content
from .ai_models import AIModelFactory

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTAssistant:
    def __init__(self, is_tour_started=False, current_page='home', model_name='4o-mini'):
        self.is_tour_started = is_tour_started
        self.current_page = current_page
        self.company = self.get_think41_company()
        self.company_info = self.get_company_info()
        self.ai_model = AIModelFactory.get_model(model_name)
        self.think41_detailed_info = self.get_think41_detailed_info()

    def get_think41_company(self):
        return Company.objects.get(name="Think41")

    def get_company_info(self):
        return CompanyInfo.objects.filter(company=self.company)

    def get_think41_detailed_info(self):
        return """
        Think41's website can be accessed at Think41.com. For career opportunities and referrals, email career@think41.com. 
        Founder profiles on LinkedIn: 
        - Anshuman Singh (https://www.linkedin.com/in/anshum4n/)
        - Harshit Singhal (https://www.linkedin.com/in/harshitsinghal01/)
        - Himanshu Varshney (https://www.linkedin.com/in/himanshuhv/)
        - Sripathi Krishnan (https://www.linkedin.com/in/sripathikrishnan/)
        
        Think41 is a technology consulting company providing Custom Software as a Service (CSaaS). Founded by the team behind HashedIn (acquired by Deloitte US in 2021), Think41 aims to re-imagine software development in the post-Gen AI world.
        
        Key points:
        - Offers customized software development and management as a service or subscription model
        - Utilizes an Autopod-based pricing model for transparency and flexibility
        - Employs GenAI-focused technology tools and frameworks
        - Services include cloud-native app development, Gen AI agent development, and LLM maintenance
        - Clients include Series B funded startups, mid-sized listed enterprises, and Deloitte
        - Self-funded with a $2 million investment, founded in June 2024
        
        Founder backgrounds:
        - Anshuman Singh: Expertise in technology and scalability
        - Harshit Singhal: Expanded mid-market segment for Deloitte, co-founded Auctus Advisors
        - Himanshu Varshney: People-oriented leader, recognized as one of India's Top 25 Trusted Leaders
        - Sripathi Krishnan: Former CTO and MD of Modern Software Engineering at Deloitte US
        
        The founders are based in Bangalore, India, with extensive travel to the Bay Area, US.
        """

    def generate_response(self, user_input):
        context = self.get_context()
        full_prompt = f"""{context}
        Current page: {self.current_page}
        Tour started: {"Yes" if self.is_tour_started else "No"}
        
        Additional Think41 Information:
        {self.think41_detailed_info}
        
        User: {user_input}
        Virtual Concierge:"""
        
        response = self.ai_model.generate_response(full_prompt)
        
        if isinstance(response, dict) and 'choices' in response:
            ai_response = response['choices'][0]['message']['content']
        elif isinstance(response, str):
            ai_response = response
        else:
            ai_response = "I'm sorry, but I couldn't generate a response at this time."

        return {
            "response": ai_response,
            "current_page": self.current_page,
            "is_tour_started": self.is_tour_started
        }

    def get_context(self):
        context = self.get_company_context()
        context += self.get_chatbot_context()
        return context

    def get_company_context(self):
        context = f"You are a virtual assistant for {self.company.name}. "
        context += f"About the company: {self.company.description}\n"
        context += f"Industry: {self.company.industry}\n"
        context += f"Founded: {self.company.founded_year}\n"
        context += f"Website: {self.company.website}\n"
        
        for info in self.company_info:
            if info.is_public:
                context += f"{info.key}: {info.value}\n"
        
        return context

    def get_chatbot_context(self):
        return f"""The user is currently on the '{self.current_page}' page. Your role is to:
        1. Provide information about the current page and its content.
        2. {"Continue guiding the user through the tour." if self.is_tour_started else "Offer to start a tour of the website if they haven't begun one."}
        3. Answer any questions about our company, products, services, or founders.
        4. Suggest relevant pages, videos, or blog posts based on their interests.
        5. Keep the conversation engaging and hospitable.
        6. Encourage exploration of different sections of the website.
        7. Emphasize Think41's unique selling points and how they differentiate from competitors.
        8. Relate responses to Think41's specific products and services when relevant.
        9. Use Think41's tone and style in responses, maintaining a professional yet approachable demeanor."""

def gpt_assistant(prompt, prompt_type='create', model_name='4o-mini'):  # Changed default to '4o-mini'
    assistant = GPTAssistant(model_name=model_name)
    return assistant.generate_response(prompt, prompt_type)