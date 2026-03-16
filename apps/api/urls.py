from django.urls import path
from .views import HealthCheckView, InventoryView, PurchaseOrdersView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('inventory/', InventoryView.as_view(), name='inventory'),
    path('purchase-orders/', PurchaseOrdersView.as_view(), name='purchase_orders'),
]
