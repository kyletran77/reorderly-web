from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='WaitlistEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('shopify_store', models.CharField(blank=True, max_length=200)),
                ('sku_count', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(default='landing', max_length=100)),
            ],
            options={
                'verbose_name': 'Waitlist Entry',
                'verbose_name_plural': 'Waitlist Entries',
                'ordering': ['-created_at'],
            },
        ),
    ]
