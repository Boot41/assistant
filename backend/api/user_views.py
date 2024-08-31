from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
import json

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