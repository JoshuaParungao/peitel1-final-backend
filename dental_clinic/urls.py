"""
URL configuration for dental_clinic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from clinic import views as clinic_views
from clinic.admin import custom_admin_site
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response

# Root API endpoint
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request):
    """API root - redirects to clinic endpoints"""
    return Response({
        'message': 'Dental Clinic POS API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/clinic/api/health/',
            'services': '/clinic/api/services/',
            'login': '/clinic/api/login/',
            'register': '/clinic/api/register/',
            'docs': '/clinic/api-guide.html'
        }
    }, status=status.HTTP_200_OK)

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('api/', api_root, name='api_root'),
    path('api/', include('clinic.urls_api')),
    path('accounts/login/', clinic_views.login_view, name='login'),
    path('accounts/logout/', clinic_views.logout_view, name='logout'),
    path('', clinic_views.login_view, name='index'),
    path('clinic/', include('clinic.urls')),
]
