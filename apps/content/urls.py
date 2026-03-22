from django.urls import path
from . import views

urlpatterns = [
    path('', views.content_index, name='content_index'),
    path('how-to-post-on-tiktok-every-day-without-burning-out/', views.post_tiktok_daily, name='post_tiktok_daily'),
    path('ai-tools-to-automate-youtube-shorts-2026/', views.ai_tools_youtube_shorts, name='ai_tools_youtube_shorts'),
    path('how-long-does-it-take-to-make-a-youtube-short/', views.how_long_youtube_short, name='how_long_youtube_short'),
    path('opus-clip-alternatives-2026/', views.opus_clip_alternatives, name='opus_clip_alternatives'),
    path('how-to-grow-on-tiktok-as-a-small-business/', views.grow_tiktok_small_business, name='grow_tiktok_small_business'),
]
