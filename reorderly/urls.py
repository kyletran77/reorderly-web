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
    path('app/', TemplateView.as_view(template_name='react_app.html')),
    path('app/<path:subpath>', TemplateView.as_view(template_name='react_app.html')),
    path('tools/', include('apps.tools.urls')),
    path('resources/', include('apps.content.urls')),
    path('', include('apps.core.urls')),
]
