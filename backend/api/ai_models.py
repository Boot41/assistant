import os
import json
import logging
import requests
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import openai

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModel(ABC):
    @abstractmethod
    def generate_response(self, content):
        pass

class GroqModel(AIModel):
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "mixtral-8x7b-32768"

    def generate_response(self, content):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "temperature": 0.7,
            "max_tokens": 150
        }
        try:
            logger.info(f"Sending request to Groq API: {json.dumps(data)[:500]}...")
            response = requests.post(self.url, headers=headers, json=data)
            logger.info(f"Groq API response status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"Groq API response: {response.text[:500]}...")
                return response.json()
            else:
                logger.error(f"Failed to call Groq API: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.exception(f"Error in Groq API call: {str(e)}")
            return None

class GPT4Model(AIModel):
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4"

    def generate_response(self, content):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "temperature": 0.7,
            "max_tokens": 150
        }
        try:
            logger.info(f"Sending request to OpenAI API: {json.dumps(data)[:500]}...")
            response = requests.post(self.url, headers=headers, json=data)
            logger.info(f"OpenAI API response status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"OpenAI API response: {response.text[:500]}...")
                return response.json()
            else:
                logger.error(f"Failed to call OpenAI API: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.exception(f"Error in OpenAI API call: {str(e)}")
            return None

class GPT4oMiniModel(AIModel):
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = os.getenv('LITE_BASE_URL')
        self.model = "4o-mini"

    def generate_response(self, content):
        try:
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            logger.info(f"Sending request to GPT 4o-mini API: {content[:500]}...")
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}]
            )
            logger.info(f"GPT 4o-mini API response received: {response}")
            logger.info(f"Response content: {response.choices[0].message.content}")
            return response.choices[0].message.content
        except Exception as e:
            logger.exception(f"Error in GPT 4o-mini API call: {str(e)}")
            return None

class AIModelFactory:
    @staticmethod
    def get_model(model_name):
        if model_name.lower() == 'groq':
            return GroqModel()
        elif model_name.lower() == 'gpt4':
            return GPT4Model()
        elif model_name.lower() == '4o-mini':
            return GPT4oMiniModel()
        else:
            raise ValueError(f"Unsupported model: {model_name}")