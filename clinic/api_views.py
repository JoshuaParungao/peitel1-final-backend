# Mobile API Views for React Native App
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Patient, Service, Invoice, InvoiceItem, StaffProfile
from .serializers import (
    UserSerializer, PatientSerializer, ServiceSerializer, 
    InvoiceSerializer, InvoiceDetailSerializer
)
from .forms import StaffRegistrationForm


# ===== AUTHENTICATION API =====
class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints for mobile app"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login user and return token"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is staff and approved
        if not user.is_staff:
            return Response(
                {'error': 'User is not staff'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user is active (approved)
        if not user.is_active:
            return Response(
                {'error': 'Account pending admin approval'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get or create token
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=user)
        
        # Check if approved (using staff_profile if exists)
        is_approved = user.is_active
        try:
            if hasattr(user, 'staff_profile'):
                is_approved = user.staff_profile.approved and user.is_active
        except:
            is_approved = user.is_active
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_approved': is_approved,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
            }
        })
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register new staff user"""
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        # Validate required fields
        if not all([username, email, password]):
            return Response(
                {'error': 'Username, email, and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if email exists
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate password (minimum 8 characters, not all numeric)
        if len(password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if password.isdigit():
            return Response(
                {'error': 'Password cannot be entirely numeric'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True,
                is_active=False,  # Require approval
            )
            
            # Create staff profile
            StaffProfile.objects.create(
                user=user,
                position='other',
                approved=False,
            )
            
            return Response({
                'message': 'Registration successful! Your account is pending admin approval.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user (delete token)"""
        try:
            from rest_framework.authtoken.models import Token
            request.user.auth_token.delete()
            return Response({'message': 'Logged out successfully'})
        except:
            return Response(
                {'error': 'Logout failed'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ===== PATIENTS API =====
class PatientViewSet(viewsets.ModelViewSet):
    """Patient management API"""
    queryset = Patient.objects.filter(is_archived=False)
    serializer_class = PatientSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by search term"""
        queryset = Patient.objects.filter(is_archived=False)
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            ) | queryset.filter(
                contact_number__icontains=search
            )
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create patient and set created_by"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def request_archive(self, request, pk=None):
        """Soft delete patient"""
        patient = self.get_object()
        patient.is_archived = True
        patient.save()
        return Response({'message': 'Patient archived'})


# ===== SERVICES API =====
class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Services listing API (read-only)"""
    queryset = Service.objects.filter(is_archived=False, active=True)
    serializer_class = ServiceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


# ===== INVOICES API =====
class InvoiceViewSet(viewsets.ModelViewSet):
    """Invoice management API"""
    queryset = Invoice.objects.filter(is_archived=False)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InvoiceDetailSerializer
        return InvoiceSerializer
    
    def get_queryset(self):
        """Filter by patient if provided"""
        queryset = Invoice.objects.filter(is_archived=False)
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset.order_by('-date_created')
    
    def perform_create(self, serializer):
        """Create invoice and set created_by"""
        invoice = serializer.save(created_by=self.request.user)
        
        # Create invoice items from services data
        services = self.request.data.get('services', [])
        for service_data in services:
            service_id = service_data.get('service')
            quantity = service_data.get('quantity', 1)
            
            try:
                service = Service.objects.get(id=service_id)
                InvoiceItem.objects.create(
                    invoice=invoice,
                    service=service,
                    quantity=quantity,
                    price_at_time=service.price,
                    service_name_at_time=service.name
                )
            except Service.DoesNotExist:
                pass
    
    @action(detail=True, methods=['get'])
    def receipt_pdf(self, request, pk=None):
        """Download invoice as PDF"""
        from django.http import FileResponse
        from django.template.loader import render_to_string
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from io import BytesIO
        
        invoice = self.get_object()
        
        try:
            # Simple PDF generation
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)
            
            # Add invoice details
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(50, 750, f"Invoice #{invoice.id}")
            
            pdf.setFont("Helvetica", 10)
            pdf.drawString(50, 730, f"Patient: {invoice.patient}")
            pdf.drawString(50, 710, f"Date: {invoice.date_created.strftime('%Y-%m-%d')}")
            
            # Add items
            y = 680
            pdf.drawString(50, y, "Item | Price | Qty | Total")
            y -= 20
            
            for item in invoice.items.all():
                total = item.total_price()
                line = f"{item.service_name_at_time} | {item.price_at_time} | {item.quantity} | {total}"
                pdf.drawString(50, y, line)
                y -= 15
            
            # Add total
            pdf.setFont("Helvetica-Bold", 12)
            y -= 10
            total_amount = invoice.total_amount()
            pdf.drawString(50, y, f"Total: ₱{total_amount:.2f}")
            
            pdf.save()
            buffer.seek(0)
            
            response = FileResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
