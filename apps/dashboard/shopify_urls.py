from django.urls import path
from . import views

# These URLs are mounted at /shopify/
urlpatterns = [
    path('', views.shopify_install, name='shopify_install'),
    path('callback/', views.shopify_callback, name='shopify_callback'),
]
