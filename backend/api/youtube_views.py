import re
import pywhatkit as kit
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import pdb

def extract_yt_term(command):
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern, command, re.IGNORECASE)
    return match.group(1) if match else None

def get_youtube_url(search_term):
    try:
        url = kit.playonyt(search_term, open_video=False)
        return url
    except Exception as e:
        print(f"Error getting YouTube URL: {str(e)}")
        return None

@csrf_exempt
@require_http_methods(["POST"])
def handle_youtube_command(request):
    try:
        data = json.loads(request.body)
        query = data.get('query', '')

        search_term = extract_yt_term(query)
        if search_term:
            url = get_youtube_url(search_term)
            if url:
                return JsonResponse({
                    "status": "success",
                    "message": f"Found YouTube video for {search_term}",
                    "search_term": search_term,
                    "youtube_url": url
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Failed to get YouTube URL"
                }, status=500)
        else:
            return JsonResponse({
                "status": "error",
                "message": "Could not extract search term from the query"
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON in request body"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
