from django.urls import path
from . import views

urlpatterns = [
    path('', views.tools_index, name='tools_index'),
    path('po-email-generator/', views.po_email_generator, name='po_email_generator'),
    path('reorder-point-calculator/', views.reorder_point_calculator, name='reorder_point_calculator'),
    path('stockout-cost-calculator/', views.stockout_cost_calculator, name='stockout_cost_calculator'),
    path('days-of-supply-calculator/', views.days_of_supply_calculator, name='days_of_supply_calculator'),
    path('safety-stock-calculator/', views.safety_stock_calculator, name='safety_stock_calculator'),
    path('eoq-calculator/', views.eoq_calculator, name='eoq_calculator'),
    path('supplier-lead-time-tracker/', views.supplier_lead_time_tracker, name='supplier_lead_time_tracker'),
    path('moq-negotiation-email/', views.moq_negotiation_email, name='moq_negotiation_email'),
    path('stocky-migration-checklist/', views.stocky_migration_checklist, name='stocky_migration_checklist'),
    path('inventory-health-score/', views.inventory_health_score, name='inventory_health_score'),
    path('ad-intel/', views.ad_intel, name='ad_intel'),
    path('ad-intel/analyze/', views.api_ad_intel_analyze, name='api_ad_intel_analyze'),
]
