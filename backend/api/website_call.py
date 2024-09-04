from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .gpt_assistant import GPTAssistant
from .ai_models import AIModelFactory
import logging
import random

logger = logging.getLogger(__name__)

def generate_response_website(user_input, relevant_content, current_page, model_name):
    ai_model = AIModelFactory.get_model(model_name)
    
    context = "\n".join([f"{content.title}:\n{content.content}" for content in relevant_content])
    
    prompt = f"""You are an AI assistant for Think41, a technology consulting company with a product mindset. Your role is to provide helpful information about Think41 and assist users navigating the website. Maintain a professional, friendly, and concise tone.

Current page: {current_page}

User query: '{user_input}'

Relevant information from the database:
{context}

Guidelines:
1. Provide a concise response (50-100 words) that directly addresses the user's query.
2. Use the relevant information provided to answer the query accurately.
3. If the user asks for additional information about a section, elaborate on the details from the relevant content.
4. Focus on Think41's services, expertise, and how they can help businesses.
5. If asked about specific pages or navigation, provide clear and brief instructions.
6. For questions not related to Think41 or the website, politely redirect the conversation.
7. If the information isn't available in the context, suggest contacting Think41 for more details.

Response:"""

    ai_response = ai_model.generate_response(prompt)
    
    engagement_phrases = [
        "Is there anything else you'd like to know about Think41?",
        "How else can I assist you with information about our services?",
        "Do you have any other questions about Think41's expertise?",
        "What other aspects of our company would you like to explore?",
    ]
    
    if ai_response:
        response = f"{ai_response.strip()}\n\n{random.choice(engagement_phrases)}"
    else:
        response = "I apologize, but I'm having trouble generating a response. Is there a specific aspect of Think41 or our services you'd like to know more about?"

    return response

@csrf_exempt
@require_http_methods(["POST"])
def website_interaction(request):
    try:
        data = json.loads(request.body)
        user_input = data.get('user_input')
        current_page = data.get('current_page', 'home')
        model_name = data.get('model_name', '4o-mini')
        
        assistant = GPTAssistant(current_page=current_page, model_name=model_name)
        
        # Implement RAG by searching for relevant content
        relevant_content = assistant.search_relevant_content(user_input)
        
        # Generate response using the relevant content
        response = generate_response_website(user_input, relevant_content, current_page, model_name)

        return JsonResponse({
            'response': response,
            'current_page': current_page,
            'has_more_info': bool(relevant_content),
            'relevant_content': [
                {
                    'title': content.title,
                    'content_type': content.content_type,
                    'snippet': content.content[:100] + '...' if len(content.content) > 100 else content.content
                } for content in relevant_content
            ]
        })
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in website_interaction: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

# ... (keep the get_more_info function as is)
