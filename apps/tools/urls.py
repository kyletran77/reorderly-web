from django.urls import path
from . import views

urlpatterns = [
    path('', views.tools_index, name='tools_index'),

    # ── New Ad Tools ──────────────────────────────────────
    path('hook-generator/', views.hook_generator, name='hook_generator'),
    path('hook-generator/generate/', views.api_hook_generator, name='api_hook_generator'),

    path('human-voice-rewriter/', views.human_voice_rewriter, name='human_voice_rewriter'),
    path('human-voice-rewriter/rewrite/', views.api_human_voice_rewriter, name='api_human_voice_rewriter'),

    path('ugc-script-generator/', views.ugc_script_generator, name='ugc_script_generator'),
    path('ugc-script-generator/generate/', views.api_ugc_script_generator, name='api_ugc_script_generator'),

    path('pain-point-miner/', views.pain_point_miner, name='pain_point_miner'),
    path('pain-point-miner/mine/', views.api_pain_point_miner, name='api_pain_point_miner'),

    path('cta-generator/', views.cta_generator, name='cta_generator'),
    path('cta-generator/generate/', views.api_cta_generator, name='api_cta_generator'),

    path('headline-scorer/', views.headline_scorer, name='headline_scorer'),
    path('headline-scorer/score/', views.api_headline_scorer, name='api_headline_scorer'),

    path('roas-calculator/', views.roas_calculator, name='roas_calculator'),
    path('ad-budget-planner/', views.ad_budget_planner, name='ad_budget_planner'),
    path('ad-frequency-calculator/', views.ad_frequency_calculator, name='ad_frequency_calculator'),
    path('ad-creative-checklist/', views.ad_creative_checklist, name='ad_creative_checklist'),

    # ── Ad Intel ─────────────────────────────────────────
    path('ad-intel/', views.ad_intel, name='ad_intel'),
    path('ad-intel/analyze/', views.api_ad_intel_analyze, name='api_ad_intel_analyze'),

    # ── Legacy Inventory Tools ────────────────────────────
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
]
