import os
import secrets
import json
import requests as http_requests
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.db import transaction

from .models import Store, Supplier, ProductRule, PurchaseOrder, POLineItem, Integration, WebhookEvent
from .shopify_oauth import build_install_url, verify_hmac, exchange_token, get_shop_info, sync_products, get_inventory_levels
from .po_engine import check_reorder_triggers, create_purchase_orders_from_triggers, draft_po_email


# ─────────────────────────────────────────────
# Shopify OAuth
# ─────────────────────────────────────────────

def shopify_install(request):
    """Step 1: Merchant enters their store URL, we redirect to Shopify OAuth."""
    shop = request.GET.get('shop', '').strip().lower()
    if not shop:
        return render(request, 'dashboard/install.html')

    if not shop.endswith('.myshopify.com'):
        shop = f"{shop}.myshopify.com"

    state = secrets.token_hex(16)
    request.session['shopify_oauth_state'] = state
    request.session['shopify_shop'] = shop

    install_url = build_install_url(shop, state)
    return redirect(install_url)


def shopify_callback(request):
    """Step 2: Shopify redirects back here with code. Exchange for access token."""
    params = dict(request.GET)
    params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}

    # Verify state
    state = params.get('state', '')
    if state != request.session.get('shopify_oauth_state', ''):
        return render(request, 'dashboard/error.html', {'message': 'Invalid OAuth state. Please try again.'})

    # Verify HMAC
    params_copy = dict(params)
    if not verify_hmac(params_copy):
        return render(request, 'dashboard/error.html', {'message': 'HMAC verification failed.'})

    shop = params.get('shop', '')
    code = params.get('code', '')

    # Exchange code for access token
    access_token = exchange_token(shop, code)
    if not access_token:
        return render(request, 'dashboard/error.html', {'message': 'Failed to get access token from Shopify.'})

    # Get shop info
    shop_info = get_shop_info(shop, access_token)

    with transaction.atomic():
        # Find or create user + store
        store = Store.objects.filter(shop_domain=shop).first()

        if store:
            # Existing store — update token and log them in
            store.access_token = access_token
            store.shop_name = shop_info.get('name', '')
            store.shop_email = shop_info.get('email', '')
            store.save()
            user = store.owner
        else:
            # New install — create user + store
            email = shop_info.get('email', f"owner@{shop}")
            username = shop.replace('.myshopify.com', '').replace('.', '_')

            # Make username unique if needed
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=None,  # no password — auth via Shopify only
            )
            store = Store.objects.create(
                owner=user,
                shop_domain=shop,
                access_token=access_token,
                shop_name=shop_info.get('name', ''),
                shop_email=shop_info.get('email', ''),
                currency=shop_info.get('currency', 'USD'),
                timezone=shop_info.get('iana_timezone', 'UTC'),
            )

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect('/app/')


# ─────────────────────────────────────────────
# Dashboard — requires auth
# ─────────────────────────────────────────────

def _get_store(request):
    """Helper to get the store for the logged-in user."""
    try:
        return request.user.store
    except Store.DoesNotExist:
        return None


@login_required(login_url='/shopify/install/')
def dashboard_home(request):
    store = _get_store(request)
    if not store:
        return redirect('/shopify/install/')

    # Summary stats
    pending_pos = store.purchase_orders.filter(status=PurchaseOrder.STATUS_PENDING).count()
    sent_this_month = store.purchase_orders.filter(
        status=PurchaseOrder.STATUS_SENT,
        sent_at__month=date.today().month
    ).count()
    total_suppliers = store.suppliers.filter(is_active=True).count()
    active_rules = store.product_rules.filter(is_active=True).count()

    recent_pos = store.purchase_orders.select_related('supplier').order_by('-created_at')[:5]

    return render(request, 'dashboard/home.html', {
        'store': store,
        'pending_pos': pending_pos,
        'sent_this_month': sent_this_month,
        'total_suppliers': total_suppliers,
        'active_rules': active_rules,
        'recent_pos': recent_pos,
    })


@login_required(login_url='/shopify/install/')
def suppliers_list(request):
    store = _get_store(request)
    if not store:
        return redirect('/shopify/install/')
    suppliers = store.suppliers.filter(is_active=True).prefetch_related('product_rules')
    return render(request, 'dashboard/suppliers.html', {'store': store, 'suppliers': suppliers})


@login_required(login_url='/shopify/install/')
def supplier_create(request):
    store = _get_store(request)
    if not store:
        return redirect('/shopify/install/')

    if request.method == 'POST':
        supplier = Supplier.objects.create(
            store=store,
            name=request.POST.get('name', '').strip(),
            email=request.POST.get('email', '').strip(),
            contact_name=request.POST.get('contact_name', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            payment_terms=request.POST.get('payment_terms', 'Net 30'),
            lead_time_days=int(request.POST.get('lead_time_days', 14)),
            minimum_order_qty=int(request.POST.get('minimum_order_qty', 1)),
            currency=request.POST.get('currency', 'USD'),
            notes=request.POST.get('notes', '').strip(),
        )
        messages.success(request, f"Supplier '{supplier.name}' added.")
        return redirect('/app/suppliers/')

    return render(request, 'dashboard/supplier_form.html', {'store': store, 'action': 'Add Supplier'})


@login_required(login_url='/shopify/install/')
def supplier_edit(request, pk):
    store = _get_store(request)
    supplier = get_object_or_404(Supplier, pk=pk, store=store)

    if request.method == 'POST':
        supplier.name = request.POST.get('name', '').strip()
        supplier.email = request.POST.get('email', '').strip()
        supplier.contact_name = request.POST.get('contact_name', '').strip()
        supplier.phone = request.POST.get('phone', '').strip()
        supplier.payment_terms = request.POST.get('payment_terms', 'Net 30')
        supplier.lead_time_days = int(request.POST.get('lead_time_days', 14))
        supplier.minimum_order_qty = int(request.POST.get('minimum_order_qty', 1))
        supplier.currency = request.POST.get('currency', 'USD')
        supplier.notes = request.POST.get('notes', '').strip()
        supplier.save()
        messages.success(request, f"Supplier '{supplier.name}' updated.")
        return redirect('/app/suppliers/')

    return render(request, 'dashboard/supplier_form.html', {
        'store': store,
        'supplier': supplier,
        'action': 'Edit Supplier',
    })


@login_required(login_url='/shopify/install/')
def supplier_delete(request, pk):
    store = _get_store(request)
    supplier = get_object_or_404(Supplier, pk=pk, store=store)
    if request.method == 'POST':
        supplier.is_active = False
        supplier.save()
        messages.success(request, f"Supplier '{supplier.name}' removed.")
    return redirect('/app/suppliers/')


@login_required(login_url='/shopify/install/')
def products_list(request):
    """Products + reorder rule management."""
    store = _get_store(request)
    if not store:
        return redirect('/shopify/install/')

    rules = store.product_rules.filter(is_active=True).select_related('supplier').order_by('product_title')
    suppliers = store.suppliers.filter(is_active=True)
    return render(request, 'dashboard/products.html', {
        'store': store,
        'rules': rules,
        'suppliers': suppliers,
    })


@login_required(login_url='/shopify/install/')
def sync_shopify_products(request):
    """Sync products from Shopify and show them for rule setup."""
    store = _get_store(request)
    if not store:
        return redirect('/shopify/install/')

    products = sync_products(store.shop_domain, store.access_token)
    store.last_synced = timezone.now()
    store.save()

    suppliers = store.suppliers.filter(is_active=True)
    existing_rules = {r.shopify_variant_id for r in store.product_rules.filter(is_active=True)}

    return render(request, 'dashboard/sync_products.html', {
        'store': store,
        'products': products,
        'suppliers': suppliers,
        'existing_rules': existing_rules,
    })


@login_required(login_url='/shopify/install/')
@require_POST
def save_product_rule(request):
    """Save or update a reorder rule for a variant."""
    store = _get_store(request)
    if not store:
        return JsonResponse({'error': 'No store'}, status=400)

    variant_id = int(request.POST.get('variant_id'))
    product_id = int(request.POST.get('product_id'))
    supplier_id = request.POST.get('supplier_id')

    supplier = None
    if supplier_id:
        supplier = get_object_or_404(Supplier, pk=supplier_id, store=store)

    rule, created = ProductRule.objects.update_or_create(
        store=store,
        shopify_variant_id=variant_id,
        defaults={
            'shopify_product_id': product_id,
            'sku': request.POST.get('sku', ''),
            'product_title': request.POST.get('product_title', ''),
            'variant_title': request.POST.get('variant_title', ''),
            'reorder_point': int(request.POST.get('reorder_point', 10)),
            'reorder_quantity': int(request.POST.get('reorder_quantity', 50)),
            'unit_cost': request.POST.get('unit_cost') or None,
            'supplier': supplier,
            'is_active': True,
        }
    )

    action = 'created' if created else 'updated'
    messages.success(request, f"Rule {action} for {rule.sku}.")
    return redirect('/app/products/')


@login_required(login_url='/shopify/install/')
def purchase_orders_list(request):
    store = _get_store(request)
    if not store:
        return redirect('/shopify/install/')

    status_filter = request.GET.get('status', '')
    pos = store.purchase_orders.select_related('supplier').prefetch_related('line_items')
    if status_filter:
        pos = pos.filter(status=status_filter)

    return render(request, 'dashboard/purchase_orders.html', {
        'store': store,
        'purchase_orders': pos,
        'status_filter': status_filter,
        'status_choices': PurchaseOrder.STATUS_CHOICES,
    })


@login_required(login_url='/shopify/install/')
def purchase_order_detail(request, pk):
    store = _get_store(request)
    po = get_object_or_404(PurchaseOrder, pk=pk, store=store)
    return render(request, 'dashboard/po_detail.html', {'store': store, 'po': po})


@login_required(login_url='/shopify/install/')
@require_POST
def approve_po(request, pk):
    store = _get_store(request)
    po = get_object_or_404(PurchaseOrder, pk=pk, store=store)

    if po.status not in [PurchaseOrder.STATUS_DRAFT, PurchaseOrder.STATUS_PENDING]:
        messages.error(request, 'This PO cannot be approved.')
        return redirect(f'/app/purchase-orders/{pk}/')

    po.status = PurchaseOrder.STATUS_APPROVED
    po.approved_at = timezone.now()
    po.approved_by = request.user
    po.save()

    messages.success(request, f"PO {po.po_number} approved.")
    return redirect(f'/app/purchase-orders/{pk}/')


@login_required(login_url='/shopify/install/')
@require_POST
def send_po(request, pk):
    """Send the PO email to the supplier."""
    from .email_sender import send_po_email
    store = _get_store(request)
    po = get_object_or_404(PurchaseOrder, pk=pk, store=store)

    if po.status not in [PurchaseOrder.STATUS_APPROVED, PurchaseOrder.STATUS_DRAFT]:
        messages.error(request, 'PO must be approved before sending.')
        return redirect(f'/app/purchase-orders/{pk}/')

    success = send_po_email(po)
    if success:
        po.status = PurchaseOrder.STATUS_SENT
        po.sent_at = timezone.now()
        po.save()
        # Fire webhook
        _fire_webhook(store, 'po.sent', _po_payload(po))
        messages.success(request, f"PO {po.po_number} sent to {po.supplier.email}.")
    else:
        messages.error(request, 'Failed to send PO email. Check your SMTP settings.')

    return redirect(f'/app/purchase-orders/{pk}/')


@login_required(login_url='/shopify/install/')
@require_POST
def receive_po(request, pk):
    """Mark items as received (supports partial receives)."""
    store = _get_store(request)
    po = get_object_or_404(PurchaseOrder, pk=pk, store=store)

    for line_item in po.line_items.all():
        received_qty = int(request.POST.get(f'received_{line_item.id}', 0))
        line_item.quantity_received = min(received_qty, line_item.quantity_ordered)
        line_item.save()

    # Update PO status
    all_received = all(li.is_fully_received for li in po.line_items.all())
    if all_received:
        po.status = PurchaseOrder.STATUS_RECEIVED
    else:
        po.status = PurchaseOrder.STATUS_PARTIAL
    po.save()

    _fire_webhook(store, 'po.received', _po_payload(po))
    messages.success(request, f"PO {po.po_number} receive updated.")
    return redirect(f'/app/purchase-orders/{pk}/')


@login_required(login_url='/shopify/install/')
def run_reorder_check(request):
    """Manually trigger an inventory check and auto-draft POs."""
    store = _get_store(request)
    if not store:
        return redirect('/shopify/install/')

    if request.method == 'POST':
        # Get all active variant IDs
        rules = list(store.product_rules.filter(is_active=True))
        variant_ids = [r.shopify_variant_id for r in rules]

        if not variant_ids:
            messages.warning(request, 'No product rules configured. Add some products first.')
            return redirect('/app/products/')

        # Fetch live inventory from Shopify
        inventory = get_inventory_levels(store.shop_domain, store.access_token, variant_ids)

        # Check triggers
        triggered = check_reorder_triggers(store, inventory)

        if not triggered:
            messages.info(request, 'All inventory levels are above reorder points. No POs needed.')
            return redirect('/app/')

        # Create POs
        created_pos = create_purchase_orders_from_triggers(store, triggered)

        # Fire webhooks + notify
        for po in created_pos:
            _fire_webhook(store, 'po.drafted', _po_payload(po))
            _notify_slack(store, po)

        messages.success(request, f"{len(created_pos)} PO(s) drafted and ready for approval.")
        return redirect('/app/purchase-orders/?status=pending_approval')

    return render(request, 'dashboard/run_check.html', {'store': store})


@login_required(login_url='/shopify/install/')
def integrations(request):
    store = _get_store(request)
    if not store:
        return redirect('/shopify/install/')

    connected = {i.integration_type: i for i in store.integrations.filter(is_active=True)}
    return render(request, 'dashboard/integrations.html', {
        'store': store,
        'connected': connected,
        'zapier_webhook_url': f"/app/integrations/zapier/webhook/{store.id}/",
    })


@login_required(login_url='/shopify/install/')
@require_POST
def connect_slack(request):
    """Save Slack webhook URL."""
    store = _get_store(request)
    webhook_url = request.POST.get('webhook_url', '').strip()

    if not webhook_url.startswith('https://hooks.slack.com/'):
        messages.error(request, 'Invalid Slack webhook URL.')
        return redirect('/app/integrations/')

    Integration.objects.update_or_create(
        store=store,
        integration_type=Integration.TYPE_SLACK,
        defaults={
            'is_active': True,
            'credentials': {'webhook_url': webhook_url},
            'settings': {'channel': request.POST.get('channel', '#reorderly')},
        }
    )
    messages.success(request, 'Slack connected. You\'ll get PO approvals in Slack.')
    return redirect('/app/integrations/')


@login_required(login_url='/shopify/install/')
@require_POST
def connect_zapier(request):
    """Save Zapier webhook URL."""
    store = _get_store(request)
    webhook_url = request.POST.get('webhook_url', '').strip()

    Integration.objects.update_or_create(
        store=store,
        integration_type=Integration.TYPE_ZAPIER,
        defaults={
            'is_active': True,
            'credentials': {'webhook_url': webhook_url},
        }
    )
    messages.success(request, 'Zapier connected. PO events will trigger your Zaps.')
    return redirect('/app/integrations/')


@login_required(login_url='/shopify/install/')
def quickbooks_connect(request):
    """Initiate QuickBooks OAuth."""
    QB_CLIENT_ID = os.environ.get('QB_CLIENT_ID', '')
    QB_REDIRECT_URI = os.environ.get('APP_URL', 'https://reorderly.me') + '/app/integrations/quickbooks/callback/'
    state = secrets.token_hex(16)
    request.session['qb_oauth_state'] = state

    qb_auth_url = (
        f"https://appcenter.intuit.com/connect/oauth2"
        f"?client_id={QB_CLIENT_ID}"
        f"&redirect_uri={QB_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=com.intuit.quickbooks.accounting"
        f"&state={state}"
    )
    return redirect(qb_auth_url)


@login_required(login_url='/shopify/install/')
def quickbooks_callback(request):
    """Handle QuickBooks OAuth callback."""
    state = request.GET.get('state', '')
    if state != request.session.get('qb_oauth_state', ''):
        messages.error(request, 'Invalid QuickBooks OAuth state.')
        return redirect('/app/integrations/')

    code = request.GET.get('code', '')
    realm_id = request.GET.get('realmId', '')

    QB_CLIENT_ID = os.environ.get('QB_CLIENT_ID', '')
    QB_CLIENT_SECRET = os.environ.get('QB_CLIENT_SECRET', '')
    QB_REDIRECT_URI = os.environ.get('APP_URL', 'https://reorderly.me') + '/app/integrations/quickbooks/callback/'

    # Exchange code for tokens
    response = http_requests.post(
        'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
        auth=(QB_CLIENT_ID, QB_CLIENT_SECRET),
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': QB_REDIRECT_URI,
        }
    )

    if response.status_code != 200:
        messages.error(request, 'Failed to connect QuickBooks.')
        return redirect('/app/integrations/')

    tokens = response.json()
    store = _get_store(request)

    Integration.objects.update_or_create(
        store=store,
        integration_type=Integration.TYPE_QUICKBOOKS,
        defaults={
            'is_active': True,
            'credentials': {
                'access_token': tokens.get('access_token'),
                'refresh_token': tokens.get('refresh_token'),
                'realm_id': realm_id,
            },
        }
    )

    messages.success(request, 'QuickBooks connected. Bills will be created automatically when POs are sent.')
    return redirect('/app/integrations/')


@login_required(login_url='/shopify/install/')
def settings_view(request):
    store = _get_store(request)
    if not store:
        return redirect('/shopify/install/')

    if request.method == 'POST':
        store.shop_name = request.POST.get('shop_name', store.shop_name)
        store.save()
        messages.success(request, 'Settings saved.')
        return redirect('/app/settings/')

    return render(request, 'dashboard/settings.html', {'store': store})


def logout_view(request):
    logout(request)
    return redirect('/')


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _po_payload(po):
    return {
        'po_number': po.po_number,
        'status': po.status,
        'supplier': po.supplier.name,
        'supplier_email': po.supplier.email,
        'total_cost': str(po.total_cost),
        'line_items': [
            {
                'sku': li.sku,
                'product': li.product_title,
                'quantity': li.quantity_ordered,
            }
            for li in po.line_items.all()
        ],
        'created_at': po.created_at.isoformat(),
    }


def _fire_webhook(store, event_type, payload):
    """Fire event to Zapier or any connected webhook endpoint."""
    import requests as req
    try:
        integration = store.integrations.get(integration_type=Integration.TYPE_ZAPIER, is_active=True)
        webhook_url = integration.credentials.get('webhook_url', '')
        if webhook_url:
            response = req.post(webhook_url, json={'event': event_type, 'data': payload}, timeout=5)
            WebhookEvent.objects.create(
                store=store,
                event_type=event_type,
                payload=payload,
                endpoint_url=webhook_url,
                status_code=response.status_code,
                delivered_at=timezone.now(),
            )
    except Integration.DoesNotExist:
        pass
    except Exception:
        pass


def _notify_slack(store, po):
    """Send Slack notification for new PO requiring approval."""
    import requests as req
    try:
        integration = store.integrations.get(integration_type=Integration.TYPE_SLACK, is_active=True)
        webhook_url = integration.credentials.get('webhook_url', '')
        if not webhook_url:
            return

        items_text = '\n'.join([f"• {li.sku} × {li.quantity_ordered}" for li in po.line_items.all()])
        app_url = os.environ.get('APP_URL', 'https://reorderly.me')

        message = {
            'text': f"🛒 *New PO drafted:* {po.po_number}",
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"*Reorderly drafted a PO for your approval*\n\n*Supplier:* {po.supplier.name}\n*PO:* {po.po_number}\n*Total:* {po.supplier.currency} {po.total_cost}\n\n*Items:*\n{items_text}"
                    }
                },
                {
                    'type': 'actions',
                    'elements': [
                        {
                            'type': 'button',
                            'text': {'type': 'plain_text', 'text': '✅ Review & Approve'},
                            'url': f"{app_url}/app/purchase-orders/{po.id}/",
                            'style': 'primary',
                        }
                    ]
                }
            ]
        }
        req.post(webhook_url, json=message, timeout=5)
        po.slack_message_ts = timezone.now().isoformat()
        po.save(update_fields=['slack_message_ts'])
    except Integration.DoesNotExist:
        pass
    except Exception:
        pass
