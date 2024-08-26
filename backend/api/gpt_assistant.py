import os
import json
import logging
import requests
from dotenv import load_dotenv
from .models import TourStep, UserProgress, Quiz

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTAssistant:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.api_key = os.getenv('GROQ_API_KEY')
        self.user_progress = UserProgress.objects.get_or_create(user_id=user_id)[0]
        self.tour_steps = list(TourStep.objects.all().order_by('order'))

    def generate_response(self, prompt, prompt_type='tour_guide'):
        context = self.get_context()
        full_prompt = f"{context}\n\nUser: {prompt}\nAssistant:"
        response = self.call_groq_api(full_prompt)
        return response

    def get_context(self):
        if self.user_id is None:
            return {}  # Return empty context if no user_id is provided
        
        user_progress = UserProgress.objects.get(user_id=self.user_id)
        current_step = user_progress.current_step

        if current_step is None:
            # If there's no current step, get the first step
            next_step = TourStep.objects.order_by('order').first()
        else:
            next_step = TourStep.objects.filter(order__gt=current_step.order).order_by('order').first()

        context = f"You are a tour guide assistant. The current tour step is '{current_step.title}' on page '{current_step.page_name}'. "
        if next_step:
            context += f"The next step will be '{next_step.title}' on page '{next_step.page_name}'. "
        context += "Provide helpful information and guide the user through the tour. You can use 'navigate to [page]', 'show video [id]', or 'show image [id]' commands in your responses."
        return context

    def advance_step(self):
        if self.current_step_index < len(self.tour_steps) - 1:
            self.current_step_index += 1
            return True
        return False

    def call_groq_api(self, content):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": content}],
            "temperature": 0.7,
            "max_tokens": 150
        }
        try:
            logger.info(f"Sending request to Groq API: {json.dumps(data)[:500]}...")  # Log first 500 chars of payload
            response = requests.post(url, headers=headers, json=data)
            logger.info(f"Groq API response status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"Groq API response: {response.text[:500]}...")  # Log first 500 chars of response
                return response.json()
            else:
                logger.error(f"Failed to call Groq API: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.exception(f"Request exception in call_groq_api: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.exception(f"JSON decode error in call_groq_api: {str(e)}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error in call_groq_api: {str(e)}")
            return None

def gpt_assistant(prompt, prompt_type='create'):
    assistant = GPTAssistant()
    return assistant.generate_response(prompt, prompt_type)