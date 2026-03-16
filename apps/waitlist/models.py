from django.db import models


class WaitlistEntry(models.Model):
    email = models.EmailField(unique=True)
    shopify_store = models.CharField(max_length=200, blank=True)
    sku_count = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=100, default='landing')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Waitlist Entry'
        verbose_name_plural = 'Waitlist Entries'

    def __str__(self):
        return self.email
