from django.urls import path
from . import views

urlpatterns = [
    # Dashboard pages
    path('', views.dashboard_home, name='dashboard_home'),
    path('suppliers/', views.suppliers_list, name='suppliers_list'),
    path('suppliers/new/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    path('products/', views.products_list, name='products_list'),
    path('products/sync/', views.sync_shopify_products, name='sync_products'),
    path('products/save-rule/', views.save_product_rule, name='save_product_rule'),
    path('purchase-orders/', views.purchase_orders_list, name='purchase_orders_list'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='po_detail'),
    path('purchase-orders/<int:pk>/approve/', views.approve_po, name='approve_po'),
    path('purchase-orders/<int:pk>/send/', views.send_po, name='send_po'),
    path('purchase-orders/<int:pk>/receive/', views.receive_po, name='receive_po'),
    path('run-check/', views.run_reorder_check, name='run_reorder_check'),
    path('integrations/', views.integrations, name='integrations'),
    path('integrations/slack/connect/', views.connect_slack, name='connect_slack'),
    path('integrations/zapier/connect/', views.connect_zapier, name='connect_zapier'),
    path('integrations/quickbooks/', views.quickbooks_connect, name='qb_connect'),
    path('integrations/quickbooks/callback/', views.quickbooks_callback, name='qb_callback'),
    path('settings/', views.settings_view, name='dashboard_settings'),
    path('logout/', views.logout_view, name='logout'),
]
