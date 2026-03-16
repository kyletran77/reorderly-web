from django.urls import path
from .views import WaitlistView, WaitlistAdminView

urlpatterns = [
    path('', WaitlistView.as_view(), name='waitlist'),
    path('list/', WaitlistAdminView.as_view(), name='waitlist-admin'),
]
