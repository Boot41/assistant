from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TourStep, Company
from .gpt_assistant import GPTAssistant
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def chat_interaction(request):
    data = json.loads(request.body)
    user_input = data.get('user_input')
    current_page = data.get('current_page', 'home')
    is_tour_started = data.get('is_tour_started', False)
    model_name = data.get('model_name', '4o-mini')
    
    assistant = GPTAssistant(is_tour_started=is_tour_started,
        current_page=current_page, model_name=model_name)
    response = assistant.generate_response(user_input)

    if "navigate to next page" in user_input.lower():
        navigation_response = navigate_to_page(request)
        navigation_data = json.loads(navigation_response.content)
        if 'current_step' in navigation_data and navigation_data['current_step']:
            current_page = navigation_data['current_step']['page_name']
            response['response'] += f"\n\nGreat! Let's move to the {current_page} page. {navigation_data['current_step']['description']}"
        else:
            response['response'] += "\n\nI'm sorry, but there are no more pages in the tour. Would you like to review any specific information?"

    return JsonResponse({
        'response': response['response'],
        'current_page': current_page,
        'is_tour_started': response['is_tour_started']
    })

@csrf_exempt
def gpt_assistant_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
            prompt_type = data.get('promptType', 'create')
            
            assistant = GPTAssistant()
            response = assistant.generate_response(prompt, prompt_type)
            
            if response and 'choices' in response and len(response['choices']) > 0:
                assistant_message = response['choices'][0]['message']['content']
                return JsonResponse({
                    'response': assistant_message,
                    'usage': response.get('usage', {}),
                    'model': response.get('model', 'unknown')
                })
            else:
                logger.error(f"Unexpected response structure from Groq API: {response}")
                return JsonResponse({'error': 'Unexpected response structure from Groq API'}, status=500)
        except Exception as e:
            logger.error(f"Error in gpt_assistant_view: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@api_view(['GET'])
def get_tour_steps(request):
    try:
        company = Company.objects.get(id=5)  # Specifically get company with id 5
        steps = TourStep.objects.filter(company=company).order_by('order')
        if steps.exists():
            data = [{
                'id': step.id,
                'title': step.title,
                'description': step.description,
                'content': step.content,
                'page_name': step.page_name,
                'order': step.order,
                'section_id': step.section_id,
                'content_type': step.content_type
            } for step in steps]
            return Response(data)
        else:
            return Response({"message": "No tour steps found for this company"}, status=404)
    except Company.DoesNotExist:
        return Response({"error": "Company with id 5 not found"}, status=404)
    except Exception as e:
        logger.error(f"Error in get_tour_steps: {str(e)}", exc_info=True)
        return Response({"error": "An error occurred while fetching tour steps"}, status=500)

def get_initial_page(request):
    try:
        company = Company.objects.first()
        first_step = TourStep.objects.filter(company=company).order_by('order').first()
        if first_step:
            initial_page = first_step.page_name
        else:
            initial_page = 'home'
    except Exception as e:
        print(f"Error in get_initial_page: {e}")
        initial_page = 'home'
    
    return JsonResponse({'initial_page': initial_page})