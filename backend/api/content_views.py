from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Content

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