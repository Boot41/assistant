from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Tour related endpoints
    path('tour/start/', views.start_tour, name='start_tour'),
    path('tour/next/', views.next_tour_step, name='next_tour_step'),
    path('tour/previous/', views.previous_tour_step, name='previous_tour_step'),
    path('tour/progress/', views.get_tour_progress, name='get_tour_progress'),
    path('tour/steps/', views.get_all_tour_steps, name='get_all_tour_steps'),
    path('tour/go-to-step/', views.go_to_step, name='go_to_step'),
    path('tour/navigate/', views.navigate_to_page, name='navigate_to_page'),
    # Content related endpoints
    path('content/<str:content_type>/<int:content_id>/', views.get_content, name='get_content'),
    # Navigation related endpoints
    path('navigate/<str:page_name>/', views.navigate_to_page, name='navigate_to_page'),
    # Interaction related endpoints
    path('tour-guide/', views.tour_guide_interaction, name='tour_guide_interaction'),
    path('gpt-assistant/', views.gpt_assistant_view, name='gpt_assistant'),
    path('tour/analytics/', views.get_tour_analytics, name='get_tour_analytics'),
    path('tour/quiz-answer/', views.handle_quiz_answer, name='handle_quiz_answer'),
    path('user/points/', views.get_user_points, name='get_user_points'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)