"""
AI PO Engine — Python port of the Node.js reorder agent.
Uses Claude to draft professional purchase order emails.
"""
import os
import json
import uuid
from datetime import date, timedelta
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))


def generate_po_number(store_id: int) -> str:
    """Generate a unique PO number."""
    today = date.today().strftime('%Y%m%d')
    suffix = str(uuid.uuid4())[:6].upper()
    return f"PO-{today}-{suffix}"


def draft_po_email(store_name: str, supplier: dict, line_items: list) -> dict:
    """
    Use Claude to draft a professional PO email.

    supplier = {name, contact_name, email, payment_terms, lead_time_days, currency}
    line_items = [{sku, product_title, variant_title, quantity, unit_cost}]

    Returns {subject, body, expected_delivery}
    """
    expected_delivery = (date.today() + timedelta(days=supplier.get('lead_time_days', 14))).strftime('%B %d, %Y')
    po_number = generate_po_number(0)

    items_text = '\n'.join([
        f"  - {item['sku']} | {item['product_title']}"
        + (f" ({item['variant_title']})" if item.get('variant_title') else '')
        + f" | Qty: {item['quantity']}"
        + (f" | Unit Cost: {supplier.get('currency', 'USD')} {item['unit_cost']:.2f}" if item.get('unit_cost') else '')
        for item in line_items
    ])

    prompt = f"""Draft a professional purchase order email from {store_name} to supplier {supplier['name']}.

PO Details:
- PO Number: {po_number}
- Date: {date.today().strftime('%B %d, %Y')}
- Requested Delivery: {expected_delivery}
- Payment Terms: {supplier.get('payment_terms', 'Net 30')}
- Contact: {supplier.get('contact_name', supplier['name'])}

Line Items:
{items_text}

Write a concise, professional PO email. Include:
1. A clear subject line
2. Brief intro referencing the PO number
3. The line items in a clear format
4. Payment terms and requested delivery date
5. Brief closing with contact info placeholder

Return as JSON with keys: "subject" and "body". Keep it professional but not stiff."""

    try:
        message = client.messages.create(
            model='claude-3-5-haiku-20241022',
            max_tokens=1024,
            messages=[{'role': 'user', 'content': prompt}]
        )
        text = message.content[0].text.strip()
        # Extract JSON from response
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        result = json.loads(text)
        result['po_number'] = po_number
        result['expected_delivery'] = expected_delivery
        return result
    except Exception as e:
        # Fallback template if Claude fails
        subject = f"Purchase Order {po_number} — {store_name}"
        body = f"""Dear {supplier.get('contact_name', supplier['name'])},

Please find below our Purchase Order {po_number} dated {date.today().strftime('%B %d, %Y')}.

Items Ordered:
{items_text}

Payment Terms: {supplier.get('payment_terms', 'Net 30')}
Requested Delivery: {expected_delivery}

Please confirm receipt of this order and provide an estimated ship date.

Thank you,
{store_name}"""
        return {
            'subject': subject,
            'body': body,
            'po_number': po_number,
            'expected_delivery': expected_delivery,
        }


def check_reorder_triggers(store, inventory_levels: dict) -> list:
    """
    Given current inventory levels, find all ProductRules that should trigger a PO.
    inventory_levels = {variant_id: current_quantity}
    Returns list of triggered ProductRule objects.
    """
    from apps.dashboard.models import ProductRule, PurchaseOrder
    from django.utils import timezone
    from datetime import timedelta

    triggered = []
    active_rules = store.product_rules.filter(is_active=True).select_related('supplier')

    for rule in active_rules:
        current_qty = inventory_levels.get(rule.shopify_variant_id, None)
        if current_qty is None:
            continue

        if current_qty <= rule.reorder_point:
            # Check cooldown — don't reorder if we sent a PO in the last 7 days
            recent_po = PurchaseOrder.objects.filter(
                store=store,
                line_items__sku=rule.sku,
                created_at__gte=timezone.now() - timedelta(days=7),
                status__in=[
                    PurchaseOrder.STATUS_DRAFT,
                    PurchaseOrder.STATUS_PENDING,
                    PurchaseOrder.STATUS_APPROVED,
                    PurchaseOrder.STATUS_SENT,
                ]
            ).exists()

            if not recent_po:
                triggered.append((rule, current_qty))

    return triggered


def create_purchase_orders_from_triggers(store, triggered_rules: list) -> list:
    """
    Group triggered rules by supplier and create PurchaseOrder records.
    Returns list of created PurchaseOrder objects.
    """
    from apps.dashboard.models import PurchaseOrder, POLineItem
    from decimal import Decimal

    # Group by supplier
    by_supplier = {}
    for rule, current_qty in triggered_rules:
        if not rule.supplier:
            continue
        sup_id = rule.supplier.id
        if sup_id not in by_supplier:
            by_supplier[sup_id] = {'supplier': rule.supplier, 'rules': []}
        by_supplier[sup_id]['rules'].append((rule, current_qty))

    created_pos = []

    for sup_id, group in by_supplier.items():
        supplier = group['supplier']
        rules = group['rules']

        # Build line items for AI
        line_items_data = [
            {
                'sku': rule.sku,
                'product_title': rule.product_title,
                'variant_title': rule.variant_title,
                'quantity': rule.reorder_quantity,
                'unit_cost': float(rule.unit_cost) if rule.unit_cost else None,
            }
            for rule, _ in rules
        ]

        # Draft the PO email via Claude
        supplier_data = {
            'name': supplier.name,
            'contact_name': supplier.contact_name,
            'email': supplier.email,
            'payment_terms': supplier.payment_terms,
            'lead_time_days': supplier.lead_time_days,
            'currency': supplier.currency,
        }

        draft = draft_po_email(store.shop_name or store.shop_domain, supplier_data, line_items_data)

        # Calculate total
        total = Decimal('0')
        for rule, _ in rules:
            if rule.unit_cost:
                total += rule.unit_cost * rule.reorder_quantity

        # Create PO record
        po = PurchaseOrder.objects.create(
            store=store,
            supplier=supplier,
            po_number=draft['po_number'],
            status=PurchaseOrder.STATUS_PENDING,
            email_body=draft['body'],
            notes=f"Auto-drafted by Reorderly AI. {len(rules)} SKU(s) below reorder point.",
            total_cost=total,
        )

        # Create line items
        for rule, current_qty in rules:
            POLineItem.objects.create(
                purchase_order=po,
                product_rule=rule,
                sku=rule.sku,
                product_title=rule.product_title,
                variant_title=rule.variant_title,
                quantity_ordered=rule.reorder_quantity,
                unit_cost=rule.unit_cost,
            )

        created_pos.append(po)

    return created_pos
