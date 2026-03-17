from django.db import models
from django.contrib.auth.models import User
import uuid


class Store(models.Model):
    """A merchant's connected Shopify store."""
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store')
    shop_domain = models.CharField(max_length=255, unique=True)  # e.g. my-store.myshopify.com
    access_token = models.TextField()
    shop_name = models.CharField(max_length=255, blank=True)
    shop_email = models.EmailField(blank=True)
    currency = models.CharField(max_length=10, default='USD')
    timezone = models.CharField(max_length=100, default='UTC')
    installed_at = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.shop_domain


class Supplier(models.Model):
    """A supplier/vendor that a store orders from."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    contact_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    currency = models.CharField(max_length=10, default='USD')
    payment_terms = models.CharField(max_length=100, default='Net 30')
    lead_time_days = models.PositiveIntegerField(default=14)
    minimum_order_qty = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.store.shop_domain})"


class ProductRule(models.Model):
    """Reorder rule for a specific SKU/variant."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='product_rules')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_rules')
    shopify_variant_id = models.BigIntegerField()
    shopify_product_id = models.BigIntegerField()
    sku = models.CharField(max_length=255)
    product_title = models.CharField(max_length=255)
    variant_title = models.CharField(max_length=255, blank=True)
    reorder_point = models.IntegerField(default=10)       # trigger reorder when stock <= this
    reorder_quantity = models.IntegerField(default=50)    # how many units to order
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'shopify_variant_id')
        ordering = ['product_title', 'variant_title']

    def __str__(self):
        return f"{self.sku} — reorder @ {self.reorder_point}"


class PurchaseOrder(models.Model):
    """A purchase order drafted by the AI agent."""
    STATUS_DRAFT = 'draft'
    STATUS_PENDING = 'pending_approval'
    STATUS_APPROVED = 'approved'
    STATUS_SENT = 'sent'
    STATUS_PARTIAL = 'partially_received'
    STATUS_RECEIVED = 'received'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending Approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_SENT, 'Sent to Supplier'),
        (STATUS_PARTIAL, 'Partially Received'),
        (STATUS_RECEIVED, 'Received'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='purchase_orders')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    po_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    notes = models.TextField(blank=True)              # AI-generated notes
    email_body = models.TextField(blank=True)         # full AI-generated email
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_delivery = models.DateField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Integration tracking
    quickbooks_bill_id = models.CharField(max_length=100, blank=True)
    slack_message_ts = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"PO-{self.po_number} → {self.supplier.name}"

    @property
    def is_editable(self):
        return self.status in [self.STATUS_DRAFT, self.STATUS_PENDING]


class POLineItem(models.Model):
    """A line item on a purchase order."""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='line_items')
    product_rule = models.ForeignKey(ProductRule, on_delete=models.SET_NULL, null=True, blank=True)
    sku = models.CharField(max_length=255)
    product_title = models.CharField(max_length=255)
    variant_title = models.CharField(max_length=255, blank=True)
    quantity_ordered = models.IntegerField()
    quantity_received = models.IntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @property
    def total_cost(self):
        if self.unit_cost:
            return self.unit_cost * self.quantity_ordered
        return None

    @property
    def is_fully_received(self):
        return self.quantity_received >= self.quantity_ordered

    def __str__(self):
        return f"{self.sku} x{self.quantity_ordered}"


class Integration(models.Model):
    """A third-party integration for a store."""
    TYPE_QUICKBOOKS = 'quickbooks'
    TYPE_SLACK = 'slack'
    TYPE_ZAPIER = 'zapier'
    TYPE_GMAIL = 'gmail'
    TYPE_XERO = 'xero'

    TYPE_CHOICES = [
        (TYPE_QUICKBOOKS, 'QuickBooks Online'),
        (TYPE_SLACK, 'Slack'),
        (TYPE_ZAPIER, 'Zapier'),
        (TYPE_GMAIL, 'Gmail'),
        (TYPE_XERO, 'Xero'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='integrations')
    integration_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    credentials = models.JSONField(default=dict)   # encrypted in prod via SECRET_KEY
    settings = models.JSONField(default=dict)      # e.g. slack channel, QB company ID
    connected_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('store', 'integration_type')

    def __str__(self):
        return f"{self.store.shop_domain} → {self.integration_type}"


class WebhookEvent(models.Model):
    """Log of outbound webhook events (Zapier, etc.)."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='webhook_events')
    event_type = models.CharField(max_length=100)   # e.g. po.drafted, po.sent
    payload = models.JSONField()
    endpoint_url = models.URLField(blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
