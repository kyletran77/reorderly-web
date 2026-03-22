from django.urls import path
from . import views

urlpatterns = [
    path('', views.content_index, name='content_index'),
    path('replacing-shopify-stocky/', views.replacing_stocky, name='replacing_stocky'),
    path('automate-purchase-orders-shopify/', views.automate_pos, name='automate_pos'),
    path('how-to-calculate-reorder-point/', views.reorder_point_guide, name='reorder_point_guide'),
]
