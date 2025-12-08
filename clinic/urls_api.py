# API URLs for mobile app
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import AuthViewSet, PatientViewSet, ServiceViewSet, InvoiceViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'services', ServiceViewSet, basename='services')
router.register(r'invoices', InvoiceViewSet, basename='invoices')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]
