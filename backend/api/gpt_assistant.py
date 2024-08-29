import os
import json
import logging
import requests
from dotenv import load_dotenv
from .models import TourStep, UserProfile, Company, CompanyInfo
from .ai_models import AIModelFactory

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTAssistant:
    def __init__(self, user_id=None, model_name='4o-mini', current_page=None):
        self.user_id = user_id
        self.user_profile = UserProfile.objects.get(user_id=user_id) if user_id else None
        self.company = self.user_profile.company if self.user_profile else None
        self.tour_steps = list(TourStep.objects.filter(company=self.company).order_by('order'))
        self.ai_model = AIModelFactory.get_model(model_name)
        self.company_info = self.get_company_info()
        self.founder_info = self.get_founder_info()
        self.current_page = current_page or 'Unknown'  # Provide a default value

    def generate_response(self, user_input):
        context = self.get_context()
        full_prompt = f"""{context}
        Current page: {self.current_page}
        User: {user_input}
        Virtual Concierge: As the virtual concierge for {self.company.name if self.company else 'the company'}, I'm here to guide you through our website and answer any questions you may have. Remember, you are currently on the '{self.current_page}' page."""
        response = self.ai_model.generate_response(full_prompt)
        if response is None:
            logger.error("AI model returned None response")
            return {"error": "Failed to generate response"}
        return {"response": response}

    def get_context(self):
        context = self.get_company_context()
        if self.user_profile and self.user_profile.current_tour_step:
            context += self.get_tour_context()
        else:
            context += self.get_chatbot_context()
        return context

    def get_company_context(self):
        context = f"Company: {self.company.name if self.company else 'Unknown'}\n"
        if self.company_info:
            context += "Company Information:\n"
            for info in self.company_info:
                context += f"- {info['key']}: {info['value']}\n"
        if self.founder_info:
            context += "Founder Information:\n"
            for info in self.founder_info:
                context += f"- {info}\n"
        return context

    def get_tour_context(self):
        current_step = self.user_profile.current_tour_step
        context = f"""The user is currently on the '{self.current_page}' page, and we're at the '{current_step.title}' step of the website tour. Here's what they need to know:

        {current_step.description}

        Key points:
        {current_step.content}

        Guide the user through this step, but be ready to answer any questions they might have about the company or website. When they're ready, offer to move to the next step of the tour."""
        return context

    def get_chatbot_context(self):
        return f"""The user is currently on the '{self.current_page}' page. Your role is to:
        1. Provide information about the current page and its content.
        2. Offer to start a tour of the website if they haven't begun one.
        3. Answer any questions about our company, products, services, or founders.
        4. Suggest relevant pages, videos, or blog posts based on their interests.
        5. Keep the conversation engaging and hospitable.
        6. Encourage exploration of different sections of the website."""

    def get_generic_context(self):
        return """You are an intelligent and helpful tour guide assistant for our application. Your role is to guide users through the features and functionalities of our platform, answering questions and providing clear, concise explanations. Always maintain a friendly and professional tone."""

    def get_start_tour_context(self):
        first_step = TourStep.objects.order_by('order').first()
        if first_step:
            return f"""Welcome to the tour of our application! I'm here to guide you through each step and help you understand the key features of our platform. We'll begin with '{first_step.title}' on the {first_step.page_name} page. Are you ready to start? If you have any questions at any point, feel free to ask!"""
        else:
            return """Welcome to our application! I'm here to assist you, but it seems we don't have any specific tour steps set up at the moment. Feel free to ask any questions about our platform, and I'll do my best to help you navigate and understand our features."""

    def get_step_context(self, step):
        return f"""We are currently on the '{step.page_name}' page, focusing on '{step.title}'. Here's what you need to know:

{step.description}

Key points to remember:
1. {step.content if step.content else 'No specific content provided for this step.'}
2. This step is designed to help you understand {step.title.lower()}.
3. Take your time to explore this section and ask any questions you may have.

 """

    def get_next_step_context(self, next_step):
        return f"""Once you're comfortable with the current step, we'll move on to '{next_step.title}' on the {next_step.page_name} page. This will cover {next_step.description.split('.')[0].lower()}."""

    def get_general_instructions(self):
        return """

As we progress through the tour:
1. Use 'navigate to [page]' to move to a different page.
2. Use 'show video [id]' to display relevant video content.
3. Use 'show image [id]' to display helpful images or diagrams.
4. If you need to repeat any information or go back to a previous step, just ask.
5. Feel free to ask questions about any feature or concept you'd like clarified.

Remember, I'm here to ensure you have a comprehensive understanding of our platform. Don't hesitate to ask for more details or examples if anything is unclear."""

    def advance_step(self):
        if self.current_step_index < len(self.tour_steps) - 1:
            self.current_step_index += 1
            return True
        return False

    def get_company_info(self):
        if self.company:
            return CompanyInfo.objects.filter(company=self.company, is_public=True).values('key', 'value')
        return []

    def get_founder_info(self):
        # Implement this method based on your data model
        # For now, we'll return an empty list
        return []

    def update_current_page(self, new_page):
        self.current_page = new_page

def gpt_assistant(prompt, prompt_type='create', model_name='4o-mini'):  # Changed default to '4o-mini'
    assistant = GPTAssistant(model_name=model_name)
    return assistant.generate_response(prompt, prompt_type)