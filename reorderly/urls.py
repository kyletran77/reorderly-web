from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import JsonResponse


def health(request):
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('health/', health),
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('api/waitlist/', include('apps.waitlist.urls')),
    path('app/', include('apps.dashboard.urls')),
    path('shopify/', include('apps.dashboard.shopify_urls')),
    path('tools/', include('apps.tools.urls')),
    path('resources/', include('apps.content.urls')),
    path('directory/', include('apps.directory.urls')),
    path('', include('apps.core.urls')),
]
