from django.urls import path, include
from rest_framework.routers import DefaultRouter
from classification.views import ClassificationViewSet, UploadExcelView, BatchStatusView, ClearDataView

router = DefaultRouter()
router.register(r'classifications', ClassificationViewSet)

urlpatterns = [
    path('upload/', UploadExcelView.as_view(), name='upload-excel'),
    path('status/', BatchStatusView.as_view(), name='batch-status'),
    path('clear/', ClearDataView.as_view(), name='clear-data'),
    path('', include(router.urls)),
]
