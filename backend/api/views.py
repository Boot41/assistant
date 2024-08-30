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
from .models import TourStep, Company

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def chat_interaction(request):
    data = json.loads(request.body)
    user_input = data.get('user_input')
    current_page = data.get('current_page', 'home')
    is_tour_started = data.get('is_tour_started', False)
    model_name = data.get('model_name', '4o-mini')
    
    assistant = GPTAssistant(is_tour_started=is_tour_started, current_page=current_page, model_name=model_name)
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
        
        next_step = user_profile.current_tour_step.next_step
        next_step_data = None
        if next_step:
            next_step_data = {
                "title": next_step.title,
                "description": next_step.description,
                "page_name": next_step.page_name,
            }
        
        return JsonResponse({
            "current_step": {
                "title": user_profile.current_tour_step.title,
                "description": user_profile.current_tour_step.description,
                "page_name": user_profile.current_tour_step.page_name,
                "section_id": user_profile.current_tour_step.section_id,
                "content_type": user_profile.current_tour_step.content_type,
                "content": user_profile.current_tour_step.content
            },
            "next_step": next_step_data,
            "total_steps": total_steps,
            "current_step_number": current_step_number,
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
    try:
        data = json.loads(request.body)
        current_page = data.get('current_page')
        
        if not current_page:
            return JsonResponse({"error": "Missing current_page"}, status=400)

        # Assuming you want to use a specific company, you can set it here
        # For example, using the company with id=1 as mentioned earlier
        company = Company.objects.get(id=1)
        
        next_step = TourStep.objects.filter(company=company, page_name__gt=current_page).order_by('page_name').first()
        
        if next_step:
            return JsonResponse({
                "message": f"Navigated to {next_step.page_name}",
                "current_step": {
                    "title": next_step.title,
                    "description": next_step.description,
                    "page_name": next_step.page_name,
                    "section_id": next_step.section_id,
                    "content_type": next_step.content_type,
                    "content": next_step.content
                }
            })
        else:
            return JsonResponse({"message": "No next page available", "current_step": None})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Company.DoesNotExist:
        return JsonResponse({"error": "Company not found"}, status=404)
    except Exception as e:
        logger.error(f"Error in navigate_to_page: {str(e)}", exc_info=True)
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def start_tour(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        company = user_profile.company
        
        first_step = TourStep.objects.filter(company=company).order_by('order').first()
        if first_step:
            user_profile.current_tour_step = first_step
            user_profile.save()
            
            return JsonResponse({
                "message": "Tour started",
                "current_step": {
                    "title": first_step.title,
                    "description": first_step.description,
                    "content": first_step.content,
                    "page_name": first_step.page_name,
                    "section_id": first_step.section_id,
                    "content_type": first_step.content_type,
                },
                "current_page": first_step.page_name
            })
        else:
            return JsonResponse({"error": "No tour steps available"}, status=404)
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User profile not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def next_tour_step(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        current_step = user_profile.current_tour_step
        
        if current_step and current_step.next_step:
            user_profile.current_tour_step = current_step.next_step
            user_profile.save()
            
            return JsonResponse({
                "message": "Moved to next step",
                "current_step": {
                    "title": user_profile.current_tour_step.title,
                    "description": user_profile.current_tour_step.description,
                    "page_name": user_profile.current_tour_step.page_name,
                    "section_id": user_profile.current_tour_step.section_id,
                    "content_type": user_profile.current_tour_step.content_type,
                    "content": user_profile.current_tour_step.content
                },
                "current_page": user_profile.current_tour_step.page_name
            })
        else:
            return JsonResponse({"message": "Tour completed or no next step available"}, status=200)
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User profile not found"}, status=404)
    except Exception as e:
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
    try:
        company = Company.objects.get(id=1)  # Specifically get company with id 5
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
        # Assuming you have a way to determine the current company
        # You might need to adjust this based on your actual setup
        company = Company.objects.first()  # or some other way to get the current company
        first_step = TourStep.objects.filter(company=company).order_by('order').first()
        if first_step:
            initial_page = first_step.page_name
        else:
            initial_page = 'home'  # default if no tour steps are found
    except Exception as e:
        print(f"Error in get_initial_page: {e}")
        initial_page = 'home'  # default in case of any error
    
    return JsonResponse({'initial_page': initial_page})