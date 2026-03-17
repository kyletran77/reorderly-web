from django.urls import path
from . import views

urlpatterns = [
    path('', views.directory_index, name='directory_index'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/<slug:slug>/', views.supplier_detail, name='supplier_detail'),
    path('stores/', views.store_list, name='store_list'),
    path('stores/<slug:slug>/', views.store_detail, name='store_detail'),
]
