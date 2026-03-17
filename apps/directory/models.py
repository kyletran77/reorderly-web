from django.db import models


CATEGORY_CHOICES = [
    ('apparel', 'Apparel & Fashion'),
    ('home', 'Home & Garden'),
    ('beauty', 'Beauty & Personal Care'),
    ('sports', 'Sports & Outdoors'),
    ('electronics', 'Electronics & Accessories'),
    ('pets', 'Pet Supplies'),
    ('food', 'Food & Beverage'),
    ('toys', 'Toys & Games'),
    ('health', 'Health & Wellness'),
    ('automotive', 'Automotive'),
    ('other', 'Other'),
]

COUNTRY_CHOICES = [
    ('CN', 'China'),
    ('IN', 'India'),
    ('VN', 'Vietnam'),
    ('BD', 'Bangladesh'),
    ('TR', 'Turkey'),
    ('ID', 'Indonesia'),
    ('PK', 'Pakistan'),
    ('MX', 'Mexico'),
    ('TW', 'Taiwan'),
    ('KR', 'South Korea'),
    ('IT', 'Italy'),
    ('PT', 'Portugal'),
    ('OTHER', 'Other'),
]


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default='CN')
    city = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    # Import Yeti stats
    us_importers = models.PositiveIntegerField(default=0, help_text="Number of US companies that import from this supplier")
    total_shipments = models.PositiveIntegerField(default=0, help_text="Total US-bound shipments on record")
    annual_shipments = models.PositiveIntegerField(default=0, help_text="Estimated annual shipments")

    # Notable brands
    notable_brands = models.JSONField(default=list, blank=True, help_text="List of notable US brands/stores that use this supplier")

    # Product details
    products = models.TextField(blank=True, help_text="Types of products made")
    min_order_qty = models.CharField(max_length=100, blank=True)
    lead_time_days = models.PositiveIntegerField(null=True, blank=True)

    # Meta
    import_yeti_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-us_importers', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/directory/suppliers/{self.slug}/'

    @property
    def country_name(self):
        return dict(COUNTRY_CHOICES).get(self.country, self.country)

    @property
    def category_name(self):
        return dict(CATEGORY_CHOICES).get(self.category, self.category)


class ShopifyStore(models.Model):
    TRAFFIC_CHOICES = [
        ('small', 'Under 10K/mo visits'),
        ('medium', '10K–100K/mo visits'),
        ('large', '100K–1M/mo visits'),
        ('enterprise', '1M+/mo visits'),
    ]

    REVENUE_CHOICES = [
        ('startup', 'Under $1M ARR'),
        ('growing', '$1M–$10M ARR'),
        ('scaleup', '$10M–$50M ARR'),
        ('enterprise', '$50M+ ARR'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    url = models.URLField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    # Store stats
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    employee_count = models.CharField(max_length=50, blank=True, help_text="e.g. '50–200'")
    revenue_tier = models.CharField(max_length=20, choices=REVENUE_CHOICES, blank=True)
    annual_revenue_est = models.CharField(max_length=50, blank=True, help_text="e.g. '$2M–$5M'")
    traffic_tier = models.CharField(max_length=20, choices=TRAFFIC_CHOICES, blank=True)
    location = models.CharField(max_length=100, blank=True)
    sku_count = models.CharField(max_length=50, blank=True, help_text="e.g. '150–300'")
    supplier_count = models.CharField(max_length=50, blank=True, help_text="e.g. '5–10'")

    # Context
    notable_for = models.TextField(blank=True, help_text="What makes this store notable")
    shopify_plus = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/directory/stores/{self.slug}/'

    @property
    def category_name(self):
        return dict(CATEGORY_CHOICES).get(self.category, self.category)
