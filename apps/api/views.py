from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class HealthCheckView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'version': '0.1.0'})


class InventoryView(APIView):
    def get(self, request):
        # Placeholder — real implementation connects to Shopify Admin API
        return Response({
            'items': [],
            'message': 'Connect your Shopify store to see inventory data.'
        })


class PurchaseOrdersView(APIView):
    def get(self, request):
        # Placeholder — real implementation queries PO history
        return Response({
            'orders': [],
            'message': 'No purchase orders yet.'
        })
