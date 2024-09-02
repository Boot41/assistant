from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .tour_views import (
    start_tour, next_tour_step, previous_tour_step, get_tour_progress,
    get_all_tour_steps, go_to_step, navigate_to_page
)
from .content_views import get_content
from .user_views import user_login, user_logout
from .analytics_views import get_tour_analytics, get_detailed_analytics
from .youtube_views import handle_youtube_command
from .ppt_presenter import get_ppt_data

urlpatterns = [
    # Tour related endpoints
    path('tour/start/', start_tour, name='start_tour'),
    path('tour/next/', next_tour_step, name='next_tour_step'),
    path('tour/previous/', previous_tour_step, name='previous_tour_step'),
    path('tour/progress/', get_tour_progress, name='get_tour_progress'),
    path('tour/steps/', get_all_tour_steps, name='get_all_tour_steps'),
    path('tour/go-to-step/', go_to_step, name='go_to_step'),
    path('tour/navigate/', navigate_to_page, name='navigate_to_page'),
    # Content related endpoints
    path('content/<str:content_type>/<int:content_id>/', get_content, name='get_content'),
    # Navigation related endpoints
    path('navigate/<str:page_name>/', navigate_to_page, name='navigate_to_page'),
    # Interaction related endpoints
    path('gpt-assistant/', views.gpt_assistant_view, name='gpt_assistant'),
    path('tour/analytics/', get_tour_analytics, name='get_tour_analytics'),
    # New chat interaction endpoint
    path('chat/', views.chat_interaction, name='chat_interaction'),
    # New tour steps endpoint
    path('tour-steps/', views.get_tour_steps, name='get_tour_steps'),
    # Initial page endpoint
    path('initial-page/', views.get_initial_page, name='get_initial_page'),
    # YouTube command endpoint
    path('youtube/', handle_youtube_command, name='handle_youtube_command'),
    # User related endpoints
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    # Detailed analytics endpoint
    path('analytics/detailed/', get_detailed_analytics, name='get_detailed_analytics'),
    # Search endpoint
    path('search/', views.search_universal_content, name='search_universal_content'),
    # PPT data endpoint
    path('ppt-data/', get_ppt_data, name='get_ppt_data'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)