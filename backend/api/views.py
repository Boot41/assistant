from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TourStep, UniversalContent
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

    return JsonResponse({
        'response': response['response'],
        'current_page': current_page,
        'is_tour_started': response['is_tour_started']
    })

@csrf_exempt
@require_http_methods(["POST"])
def gpt_assistant_view(request):
    data = json.loads(request.body)
    prompt = data.get('prompt')
    model_name = data.get('model_name', '4o-mini')
    
    assistant = GPTAssistant(model_name=model_name)
    response = assistant.generate_response(prompt)

    return JsonResponse({
        'response': response['response']
    })



@api_view(['GET'])
def get_tour_steps(request):
    try:
        steps = TourStep.objects.all().order_by('order')
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
            return Response({"message": "No tour steps found"}, status=404)
    except Exception as e:
        logger.error(f"Error in get_tour_steps: {str(e)}", exc_info=True)
        return Response({"error": "An error occurred while fetching tour steps"}, status=500)

# Add a new view to search universal content
@api_view(['GET'])
def search_universal_content(request):
    query = request.GET.get('query', '')
    try:
        assistant = GPTAssistant()
        relevant_content = assistant.search_relevant_content(query)
        data = [{
            'id': content.id,
            'title': content.title,
            'content': content.content,
            'content_type': content.content_type,
            'metadata': content.metadata
        } for content in relevant_content]
        return Response(data)
    except Exception as e:
        logger.error(f"Error in search_universal_content: {str(e)}", exc_info=True)
        return Response({"error": "An error occurred while searching content"}, status=500)

def get_initial_page(request):
    initial_step = TourStep.objects.filter(is_active=True).order_by('order').first()
    if initial_step:
        return JsonResponse({
            'page_name': initial_step.page_name,
            'title': initial_step.title,
            'description': initial_step.description,
            'content': initial_step.content
        })
    else:
        return JsonResponse({'error': 'No initial page found'}, status=404)