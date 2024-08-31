from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, F, Count
from django.contrib.auth.models import User
from .models import UserProfile, TourStep
import logging

logger = logging.getLogger(__name__)

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