from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import TourStep, UserProfile, Company
import json
import logging

logger = logging.getLogger(__name__)

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

@csrf_exempt
@require_http_methods(["POST"])
def navigate_to_page(request):
    try:
        data = json.loads(request.body)
        current_page = data.get('current_page')
        
        if not current_page:
            return JsonResponse({"error": "Missing current_page"}, status=400)

        # Get the latest company (assuming the latest has the highest ID)
        latest_company = Company.objects.latest('id')
        
        next_step = TourStep.objects.filter(company=latest_company, page_name__gt=current_page).order_by('page_name').first()
        
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
    except Exception as e:
        logger.error(f"Error in navigate_to_page: {str(e)}", exc_info=True)
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)