from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('country', models.CharField(choices=[('CN', 'China'), ('IN', 'India'), ('VN', 'Vietnam'), ('BD', 'Bangladesh'), ('TR', 'Turkey'), ('ID', 'Indonesia'), ('PK', 'Pakistan'), ('MX', 'Mexico'), ('TW', 'Taiwan'), ('KR', 'South Korea'), ('IT', 'Italy'), ('PT', 'Portugal'), ('OTHER', 'Other')], default='CN', max_length=10)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('category', models.CharField(choices=[('apparel', 'Apparel & Fashion'), ('home', 'Home & Garden'), ('beauty', 'Beauty & Personal Care'), ('sports', 'Sports & Outdoors'), ('electronics', 'Electronics & Accessories'), ('pets', 'Pet Supplies'), ('food', 'Food & Beverage'), ('toys', 'Toys & Games'), ('health', 'Health & Wellness'), ('automotive', 'Automotive'), ('other', 'Other')], max_length=30)),
                ('description', models.TextField(blank=True)),
                ('us_importers', models.PositiveIntegerField(default=0, help_text='Number of US companies that import from this supplier')),
                ('total_shipments', models.PositiveIntegerField(default=0, help_text='Total US-bound shipments on record')),
                ('annual_shipments', models.PositiveIntegerField(default=0, help_text='Estimated annual shipments')),
                ('notable_brands', models.JSONField(blank=True, default=list, help_text='List of notable US brands/stores that use this supplier')),
                ('products', models.TextField(blank=True, help_text='Types of products made')),
                ('min_order_qty', models.CharField(blank=True, max_length=100)),
                ('lead_time_days', models.PositiveIntegerField(blank=True, null=True)),
                ('import_yeti_url', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('featured', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-us_importers', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ShopifyStore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('url', models.URLField()),
                ('category', models.CharField(choices=[('apparel', 'Apparel & Fashion'), ('home', 'Home & Garden'), ('beauty', 'Beauty & Personal Care'), ('sports', 'Sports & Outdoors'), ('electronics', 'Electronics & Accessories'), ('pets', 'Pet Supplies'), ('food', 'Food & Beverage'), ('toys', 'Toys & Games'), ('health', 'Health & Wellness'), ('automotive', 'Automotive'), ('other', 'Other')], max_length=30)),
                ('description', models.TextField(blank=True)),
                ('founded_year', models.PositiveIntegerField(blank=True, null=True)),
                ('employee_count', models.CharField(blank=True, help_text="e.g. '50–200'", max_length=50)),
                ('revenue_tier', models.CharField(blank=True, choices=[('startup', 'Under $1M ARR'), ('growing', '$1M–$10M ARR'), ('scaleup', '$10M–$50M ARR'), ('enterprise', '$50M+ ARR')], max_length=20)),
                ('traffic_tier', models.CharField(blank=True, choices=[('small', 'Under 10K/mo visits'), ('medium', '10K–100K/mo visits'), ('large', '100K–1M/mo visits'), ('enterprise', '1M+/mo visits')], max_length=20)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('notable_for', models.TextField(blank=True, help_text='What makes this store notable')),
                ('shopify_plus', models.BooleanField(default=False)),
                ('featured', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
