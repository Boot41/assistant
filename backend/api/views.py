from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import TourStep, Content, UserProfile, UserHistory, Company, CompanyInfo
import json
from .gpt_assistant import GPTAssistant
from django.db.models import Avg, F, Count
import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def chat_interaction(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    user_input = data.get('user_input')
    current_page = data.get('current_page')

    assistant = GPTAssistant(user_id)
    response = assistant.generate_response(user_input, current_page)

    if 'error' in response:
        return JsonResponse({'error': response['error']}, status=500)

    assistant_message = response['response']
    actions = extract_actions(assistant_message)

    # Update user history
    if user_id:
        user_profile = UserProfile.objects.get(user_id=user_id)
        UserHistory.objects.create(
            user=user_profile.user,
            company=user_profile.company,
            tour_step=user_profile.current_tour_step
        )

    return JsonResponse({
        'response': assistant_message,
        'actions': actions
    })

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
    if "show blog content" in message.lower():
        actions.append({"type": "show_blog_content"})
    return actions

@require_http_methods(["GET"])
def get_tour_progress(request):
    user_id = request.GET.get('user_id')
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        company = user_profile.company
        total_steps = TourStep.objects.filter(company=company).count()
        
        if total_steps == 0:
            return JsonResponse({
                "error": "No tour steps available for this company",
                "total_steps": 0,
                "message": "Please add tour steps to the database."
            }, status=404)

        if not user_profile.current_tour_step:
            first_step = TourStep.objects.filter(company=company).order_by('order').first()
            if first_step:
                user_profile.current_tour_step = first_step
                user_profile.save()
            else:
                return JsonResponse({"error": "No tour steps available", "total_steps": 0}, status=404)
        
        current_step_number = TourStep.objects.filter(company=company, order__lte=user_profile.current_tour_step.order).count()
        
        return JsonResponse({
            "current_step": {
                "title": user_profile.current_tour_step.title,
                "description": user_profile.current_tour_step.description,
                "page_name": user_profile.current_tour_step.page_name,
                "section_id": user_profile.current_tour_step.section_id,
                "content_type": user_profile.current_tour_step.content_type,
                "content": user_profile.current_tour_step.content
            },
            "total_steps": total_steps,
            "progress_percentage": (current_step_number / total_steps) * 100 if total_steps > 0 else 0
        })
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User profile not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

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

@csrf_exempt
@require_http_methods(["POST"])
def navigate_to_page(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    page_name = data.get('page_name')
    
    user_progress = UserProfile.objects.get(user_id=user_id)
    next_step = TourStep.objects.filter(page_name__iexact=page_name).order_by('order').first()
    
    total_steps = TourStep.objects.count()
    
    if next_step:
        user_progress.current_step = next_step
        user_progress.save()
        
        progress_percentage = (next_step.order / total_steps) * 100
        
        return JsonResponse({
            "message": f"Navigated to {page_name}",
            "current_step": {
                "id": next_step.id,
                "title": next_step.title,
                "description": next_step.description,
                "page_name": next_step.page_name,
                "section_id": next_step.section_id,
                "content_type": next_step.content_type,
                "content": next_step.content,
                "order": next_step.order
            },
            "progress_percentage": progress_percentage
        })
    else:
        progress_percentage = (user_progress.current_step.order / total_steps) * 100 if user_progress.current_step else 0
        return JsonResponse({
            "message": f"No tour step found for page {page_name}",
            "current_step": None,
            "progress_percentage": progress_percentage
    })

@csrf_exempt
@require_http_methods(["POST"])
def start_tour(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')

    total_steps = TourStep.objects.count()
    if total_steps == 0:
        return JsonResponse({
            "message": "No tour steps available. Please add tour steps to the database.",
            "tour_started": False,
            "total_steps": 0
        }, status=400)

    first_step = TourStep.objects.order_by('order').first()
    user_progress, created = UserProfile.objects.get_or_create(
        user_id=user_id,
        defaults={'current_step': first_step}
    )

    if not created and user_progress.current_step is None:
        user_progress.current_step = first_step
        user_progress.save()

    return JsonResponse({
        "message": "Tour started successfully",
        "tour_started": True,
        "current_step": {
            "id": first_step.id,
            "title": first_step.title,
            "description": first_step.description,
            "page_name": first_step.page_name,
            "order": first_step.order,
            "content_type": first_step.content_type,
            "content": first_step.content
        },
        "total_steps": total_steps
    })

@require_http_methods(["POST"])
@csrf_exempt
def next_tour_step(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        logger.info(f"Fetching next tour step for user: {user_id}")
        
        user_progress, created = UserProfile.objects.get_or_create(user_id=user_id)
        
        if created or not user_progress.current_step:
            next_step = TourStep.objects.order_by('order').first()
        else:
            next_step = TourStep.objects.filter(order__gt=user_progress.current_step.order).order_by('order').first()
        
        if next_step:
            user_progress.current_step = next_step
            user_progress.save()
            
            total_steps = TourStep.objects.count()
            progress_percentage = (next_step.order / total_steps) * 100
            
            return JsonResponse({
                "message": "Next step",
                "current_step": {
                    "id": next_step.id,
                    "title": next_step.title,
                    "description": next_step.description,
                    "page_name": next_step.page_name,
                    "section_id": next_step.section_id,
                    "content_type": next_step.content_type,
                    "content": next_step.content,
                    "order": next_step.order
                },
                "progress_percentage": progress_percentage
            })
        else:
            return JsonResponse({
                "message": "Tour completed",
                "progress_percentage": 100
            })
    except Exception as e:
        logger.error(f"Error in next_tour_step: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def get_tour_analytics(request):
    try:
        total_users = UserProfile.objects.count()
        completed_tours = UserProfile.objects.filter(current_step__isnull=True).count()
        average_progress = UserProfile.objects.exclude(current_step__isnull=True).aggregate(
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
        "content_type": step.content_type,
        "content": step.content
    } for step in steps], safe=False)

@require_http_methods(["POST"])
@csrf_exempt
def go_to_step(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    step_order = data.get('step_order')
    user_progress = UserProfile.objects.get(user_id=user_id)
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
            "content_type": step.content_type,
            "content": step.content
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
    
    quiz = Quiz.objects.get(id=question_id)
    is_correct = answer == quiz.correct_answer
    
    user_points, _ = UserProfile.objects.get_or_create(user_id=user_id)
    if is_correct:
        user_points.points += 10
        user_points.save()
    
    return JsonResponse({
        "is_correct": is_correct,
        "feedback": "Correct! You earned 10 points." if is_correct else "Sorry, that's not correct. Try again!",
        "current_points": user_points.points
    })

@require_http_methods(["GET"])
def get_user_points(request):
    user_id = request.GET.get('user_id')
    user_points, _ = UserProfile.objects.get_or_create(user_id=user_id)
    return JsonResponse({"points": user_points.points})

@require_http_methods(["POST"])
@csrf_exempt
def previous_tour_step(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        user_progress = UserProfile.objects.get(user_id=user_id)
        
        previous_step = TourStep.objects.filter(order__lt=user_progress.current_step.order).order_by('-order').first()
        
        if previous_step:
            user_progress.current_step = previous_step
            user_progress.save()
            
            total_steps = TourStep.objects.count()
            progress_percentage = (previous_step.order / total_steps) * 100
            
            return JsonResponse({
                "message": "Previous step",
                "current_step": {
                    "id": previous_step.id,
                    "title": previous_step.title,
                    "description": previous_step.description,
                    "page_name": previous_step.page_name,
                    "section_id": previous_step.section_id,
                    "content_type": previous_step.content_type,
                    "content": previous_step.content,
                    "order": previous_step.order
                },
                "progress_percentage": progress_percentage
            })
        else:
            return JsonResponse({
                "message": "No previous step available",
                "progress_percentage": 0
            })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["POST"])
def user_login(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"message": "Login successful"})
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=400)

@require_http_methods(["POST"])
def user_logout(request):
    logout(request)
    return JsonResponse({"message": "Logout successful"})

@require_http_methods(["GET"])
def get_detailed_analytics(request):
    try:
        total_users = User.objects.count()
        completed_tours = UserProfile.objects.filter(current_step__isnull=True).count()
        average_progress = UserProfile.objects.exclude(current_step__isnull=True).aggregate(
            avg_progress=Avg(F('current_step__order') * 100.0 / TourStep.objects.count())
        )['avg_progress'] or 0
        
        step_engagement = TourStep.objects.annotate(
            view_count=Count('userhistory')
        ).values('title', 'view_count')
        
        content_type_preference = UserProfile.objects.values('preferred_content_type').annotate(
            count=Count('preferred_content_type')
        )

        return JsonResponse({
            "total_users": total_users,
            "completed_tours": completed_tours,
            "average_progress": round(average_progress, 2),
            "step_engagement": list(step_engagement),
            "content_type_preference": list(content_type_preference)
        })
    except Exception as e:
        logger.error(f"Error in get_detailed_analytics: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred while fetching analytics'}, status=500)

@api_view(['GET'])
def get_tour_steps(request):
    steps = TourStep.objects.all().order_by('order')
    data = [{'title': step.title, 'description': step.description, 'content': step.content} for step in steps]
    return Response(data)