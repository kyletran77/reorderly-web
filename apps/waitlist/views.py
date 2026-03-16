import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import AllowAny
from .models import WaitlistEntry
from .serializers import WaitlistEntrySerializer


class WaitlistView(APIView):
    authentication_classes = []  # No auth — public endpoint, disables CSRF enforcement
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = WaitlistEntrySerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            # Check for existing entry
            if WaitlistEntry.objects.filter(email=email).exists():
                return Response(
                    {'message': "You're already on the waitlist! We'll be in touch soon."},
                    status=status.HTTP_200_OK
                )

            serializer.save()
            return Response(
                {'message': "You're on the list! We'll reach out when your spot is ready."},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class WaitlistAdminView(APIView):
    """Simple read-only admin endpoint — protected by secret key env var."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        secret = request.query_params.get('key', '')
        if secret != os.environ.get('ADMIN_SECRET', ''):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        entries = WaitlistEntry.objects.all().values('email', 'shopify_store', 'sku_count', 'source', 'created_at')
        return Response({'count': len(entries), 'entries': list(entries)})
