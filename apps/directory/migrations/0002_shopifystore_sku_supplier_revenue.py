from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopifystore',
            name='annual_revenue_est',
            field=models.CharField(blank=True, help_text="e.g. '$2M–$5M'", max_length=50),
        ),
        migrations.AddField(
            model_name='shopifystore',
            name='sku_count',
            field=models.CharField(blank=True, help_text="e.g. '150–300'", max_length=50),
        ),
        migrations.AddField(
            model_name='shopifystore',
            name='supplier_count',
            field=models.CharField(blank=True, help_text="e.g. '5–10'", max_length=50),
        ),
    ]
