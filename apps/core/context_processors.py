from django.conf import settings


def analytics(request):
    return {
        'ga4_id': getattr(settings, 'GA4_MEASUREMENT_ID', ''),
        'gsc_verification': getattr(settings, 'GSC_VERIFICATION', ''),
        'clarity_id': getattr(settings, 'CLARITY_ID', ''),
        'sentry_dsn': getattr(settings, 'SENTRY_DSN', ''),
    }
