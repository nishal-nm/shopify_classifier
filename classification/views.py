from django.views.generic import TemplateView
from rest_framework import viewsets, status, views
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import action
from classification.models import Classification
from classification.serializers import ClassificationSerializer, ClassificationUpdateSerializer
import threading
import tempfile
import os
from django.core.management import call_command

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

class ClassificationViewSet(viewsets.ModelViewSet):
    queryset = Classification.objects.all().select_related('product', 'category')
    serializer_class = ClassificationSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ClassificationUpdateSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        classification = self.get_object()
        classification.status = 'APPROVED'
        classification.save()
        return Response({'status': 'approved'})

class DashboardView(TemplateView):
    template_name = 'classification/dashboard.html'

class UploadExcelView(views.APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=400)
            
        # Save file to a temporary location
        fd, temp_path = tempfile.mkstemp(suffix='.xlsx')
        with os.fdopen(fd, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        from products.models import ProductBatch
        batch = ProductBatch.objects.create(
            name=f"Import {file_obj.name}",
            status="PENDING",
            total_products=0
        )
        
        # Run import and classify in the background
        def process_file(file_path):
            try:
                call_command('import_products', file_path)
                call_command('classify_products')
            except Exception as e:
                print(f"Background processing error: {e}")
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)

        thread = threading.Thread(target=process_file, args=(temp_path,))
        thread.daemon = True
        thread.start()

        return Response({'message': 'File uploaded successfully. Processing started in the background.'})

from products.models import ProductBatch

class BatchStatusView(views.APIView):
    def get(self, request):
        batch = ProductBatch.objects.order_by('-created_at').first()
        if not batch:
            return Response({'status': 'NO_BATCH'})
        
        # We can also check how many are classified vs total to be more accurate,
        # but let's just return what we have on the batch.
        # Actually classify_products doesn't update the batch processed count, only import does.
        # Let's count unclassified products.
        from products.models import Product
        total = Product.objects.count()
        unclassified = Product.objects.exclude(classifications__status__in=["COMPLETED", "APPROVED", "REVIEW", "FAILED"]).count()
        processed = total - unclassified
        is_processing = batch.status in ['PENDING', 'PROCESSING'] or unclassified > 0
        
        return Response({
            'status': 'PROCESSING' if is_processing else 'COMPLETED',
            'total': total,
            'processed': processed,
        })

class ClearDataView(views.APIView):
    def post(self, request):
        from products.models import Product, ProductBatch
        
        Product.objects.all().delete()
        ProductBatch.objects.all().delete()
        
        return Response({'message': 'All products and classifications cleared successfully.'})
