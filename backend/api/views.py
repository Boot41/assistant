from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import TourStep, Content, UserProgress, Quiz
import json
from .gpt_assistant import GPTAssistant
from django.db.models import Avg, F, Count
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def tour_guide_interaction(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    user_input = data.get('user_input')
    current_page = data.get('current_page')

    assistant = GPTAssistant(user_id)
    prompt = f"User is on page '{current_page}'. User input: '{user_input}'. Provide a tour guide response."
    response = assistant.generate_response(prompt, 'tour_guide')

    if response and 'choices' in response and len(response['choices']) > 0:
        assistant_message = response['choices'][0]['message']['content']
        
        # Extract any actions from the assistant's response
        actions = extract_actions(assistant_message)

        return JsonResponse({
            'response': assistant_message,
            'actions': actions
        })
    else:
        return JsonResponse({'error': 'Failed to generate response'}, status=500)

def extract_actions(message):
    actions = []
    if "navigate to" in message.lower():
        target = message.split("navigate to")[-1].strip()
        actions.append({"type": "navigate", "target": target})
    if "show video" in message.lower():
        video_id = message.split("show video")[-1].strip()
        actions.append({"type": "show_video", "content": f"/api/content/video/{video_id}/"})
    if "show image" in message.lower():
        image_id = message.split("show image")[-1].strip()
        actions.append({"type": "show_image", "content": f"/api/content/image/{image_id}/"})
    return actions

@require_http_methods(["GET"])
def get_tour_progress(request):
    user_id = request.GET.get('user_id')
    user_progress = UserProgress.objects.get(user_id=user_id)
    total_steps = TourStep.objects.count()
    current_step_number = TourStep.objects.filter(order__lte=user_progress.current_step.order).count()
    return JsonResponse({
        "current_step": {
            "title": user_progress.current_step.title,
            "description": user_progress.current_step.description,
            "page_name": user_progress.current_step.page_name,
            "section_id": user_progress.current_step.section_id,
            "image": user_progress.current_step.image.url if user_progress.current_step.image else None,
            "video": user_progress.current_step.video.url if user_progress.current_step.video else None
        },
        "total_steps": total_steps,
        "progress_percentage": (current_step_number / total_steps) * 100
    })

@require_http_methods(["GET"])
def get_content(request, content_type, content_id):
    try:
        content = Content.objects.get(id=content_id, content_type=content_type)
        return JsonResponse({
            "title": content.title,
            "content": content.content,
            "type": content.content_type
        })
    except Content.DoesNotExist:
        return JsonResponse({"error": "Content not found"}, status=404)

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

@require_http_methods(["GET"])
def navigate_to_page(request, page_name):
    # This function might need to be implemented on the frontend
    # Here we just return the page name for demonstration
    return JsonResponse({"page_name": page_name})

@require_http_methods(["POST"])
@csrf_exempt
def start_tour(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    first_step = TourStep.objects.order_by('order').first()
    UserProgress.objects.update_or_create(
        user_id=user_id,
        defaults={'current_step': first_step}
    )
    return JsonResponse({
        "message": "Tour started",
        "current_step": {
            "title": first_step.title,
            "description": first_step.description,
            "page_name": first_step.page_name,
            "section_id": first_step.section_id,
            "image": first_step.image.url if first_step.image else None,
            "video": first_step.video.url if first_step.video else None
        }
    })

@require_http_methods(["POST"])
@csrf_exempt
def next_tour_step(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        logger.info(f"Fetching next tour step for user: {user_id}")
        
        user_progress, created = UserProgress.objects.get_or_create(user_id=user_id)
        
        if created or not user_progress.current_step:
            next_step = TourStep.objects.order_by('order').first()
        else:
            next_step = TourStep.objects.filter(order__gt=user_progress.current_step.order).order_by('order').first()
        
        if next_step:
            user_progress.current_step = next_step
            user_progress.save()
            
            # Check if Quiz model exists before querying
            from django.apps import apps
            if apps.is_installed('api') and apps.get_model('api', 'Quiz'):
                quiz = Quiz.objects.filter(tour_step=next_step).first()
            else:
                quiz = None
            
            total_steps = TourStep.objects.count()
            progress_percentage = (next_step.order / total_steps) * 100
            
            return JsonResponse({
                "message": "Next step",
                "current_step": {
                    "title": next_step.title,
                    "description": next_step.description,
                    "page_name": next_step.page_name,
                    "section_id": next_step.section_id,
                    "image": next_step.image.url if next_step.image else None,
                    "video": next_step.video.url if next_step.video else None
                },
                "quiz_question": {
                    "id": quiz.id,
                    "question": quiz.question,
                    "options": quiz.options
                } if quiz else None,
                "progress_percentage": progress_percentage
            })
        else:
            return JsonResponse({"message": "Tour completed"})
    except Exception as e:
        logger.error(f"Error in next_tour_step: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred while fetching the next step'}, status=500)

@require_http_methods(["GET"])
def get_tour_analytics(request):
    try:
        total_users = UserProgress.objects.count()
        completed_tours = UserProgress.objects.filter(current_step__isnull=True).count()
        average_progress = UserProgress.objects.exclude(current_step__isnull=True).aggregate(
            avg_progress=Avg(F('current_step__order') * 100.0 / TourStep.objects.count())
        )['avg_progress'] or 0

        return JsonResponse({
            "total_users": total_users,
            "completed_tours": completed_tours,
            "average_progress": round(average_progress, 2)
        })
    except Exception as e:
        logger.error(f"Error in get_tour_analytics: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred while fetching analytics'}, status=500)

@require_http_methods(["GET"])
def get_all_tour_steps(request):
    steps = TourStep.objects.all().order_by('order')
    return JsonResponse([{
        "order": step.order,
        "title": step.title,
        "description": step.description,
        "page_name": step.page_name,
        "section_id": step.section_id,
        "image": step.image.url if step.image else None,
        "video": step.video.url if step.video else None
    } for step in steps], safe=False)

@require_http_methods(["POST"])
@csrf_exempt
def go_to_step(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    step_order = data.get('step_order')
    user_progress = UserProgress.objects.get(user_id=user_id)
    step = TourStep.objects.get(order=step_order)
    user_progress.current_step = step
    user_progress.save()
    total_steps = TourStep.objects.count()
    return JsonResponse({
        "message": "Step updated",
        "current_step": {
            "title": step.title,
            "description": step.description,
            "page_name": step.page_name,
            "section_id": step.section_id,
            "image": step.image.url if step.image else None,
            "video": step.video.url if step.video else None
        },
        "progress_percentage": (step_order / total_steps) * 100
    })

@require_http_methods(["POST"])
@csrf_exempt
def handle_quiz_answer(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    # Here you would implement the logic to check the answer and provide feedback
    # For now, we'll just return a simple response
    
    return JsonResponse({
        "feedback": f"Your answer '{answer}' has been recorded. Thank you for participating in the quiz!"
    })