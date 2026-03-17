from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('stocky-alternative/', views.stocky_alternative, name='stocky_alternative'),
    path('pricing/', views.pricing, name='pricing'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('robots.txt', views.robots, name='robots'),
]
