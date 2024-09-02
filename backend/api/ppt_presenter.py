from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import PPTSlide

@require_http_methods(["GET"])
def get_ppt_data(request):
    try:
        slides = PPTSlide.objects.all().order_by('order')
        data = [{
            "title": slide.title,
            "content": slide.content,
            "transcript": slide.transcript,
            "order": slide.order
        } for slide in slides]
        ppt_url = "https://docs.google.com/presentation/d/1HQebyXLjktgpq8eF0PZSHeeRLDknu_bzGq95_E3xpkA/edit?usp=sharing"
        return JsonResponse({"ppt_url": ppt_url, "ppt_data": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
