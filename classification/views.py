from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from classification.models import Classification
from classification.serializers import ClassificationSerializer, ClassificationUpdateSerializer

class ClassificationViewSet(viewsets.ModelViewSet):
    queryset = Classification.objects.all().select_related('product', 'category')
    serializer_class = ClassificationSerializer
    
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
