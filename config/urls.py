"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from classification.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('classification.urls')),
    path('', DashboardView.as_view(), name='dashboard'),
]
