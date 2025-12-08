from django.urls import path
from . import views
from .auth_views import FrontendLoginView, FrontendRegistrationView, FrontendLogoutView, StaffLoginView

app_name = 'clinic'

urlpatterns = [
    # Authentication
    path('login/', FrontendLoginView.as_view(), name='login'),
    path('register/', FrontendRegistrationView.as_view(), name='register'),
    path('logout/', FrontendLogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Patients Module
    path('patients/', views.patients_list, name='patients_list'),
    path('patients/create/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/update/', views.patient_update, name='patient_update'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),

    # Services Module
    path('services/', views.services_list, name='services_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/<int:pk>/update/', views.service_update, name='service_update'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),

    # Invoices Module
    path('invoices/', views.invoices_list, name='invoices_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/update/', views.invoice_update, name='invoice_update'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),

    # Archive Module
    path('archive/', views.archive, name='archive'),
    path('archive/patient/<int:pk>/restore/', views.restore_patient, name='restore_patient'),
    path('archive/patient/<int:pk>/delete/', views.delete_patient_permanent, name='delete_patient_permanent'),
    path('archive/service/<int:pk>/restore/', views.restore_service, name='restore_service'),
    path('archive/service/<int:pk>/delete/', views.delete_service_permanent, name='delete_service_permanent'),
    path('archive/staff/<int:pk>/restore/', views.restore_staff, name='restore_staff'),
    path('archive/staff/<int:pk>/delete/', views.delete_staff_permanent, name='delete_staff_permanent'),
    path('archive/invoice/<int:pk>/restore/', views.restore_invoice, name='restore_invoice'),
    path('archive/invoice/<int:pk>/delete/', views.delete_invoice_permanent, name='delete_invoice_permanent'),

    # Staff Approval Module
    path('staff/approval/', views.staff_approval, name='staff_approval'),
    path('staff/approval/<int:pk>/approve/', views.approve_staff, name='approve_staff'),
    path('staff/approval/<int:pk>/reject/', views.reject_staff, name='reject_staff'),
    
    # Staff List with Activity
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/<int:pk>/delete/', views.staff_delete, name='staff_delete'),
    # Staff POS (mobile)
    path('staff/login/', StaffLoginView.as_view(), name='staff_login'),
    path('staff/pos/', views.staff_pos, name='staff_pos'),
    
    # Sales Analytics
    path('sales/analytics/', views.sales_analytics, name='sales_analytics'),
]
