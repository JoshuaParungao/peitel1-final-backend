from rest_framework import serializers
from .models import Service, Patient, Invoice, InvoiceItem
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff']
        read_only_fields = ['id']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'category', 'name', 'description', 'price', 'active']


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'contact_number', 'email', 'address', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class InvoiceItemSerializer(serializers.ModelSerializer):
    service_name_at_time = serializers.CharField(read_only=True)
    price_at_time = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = InvoiceItem
        fields = ['id', 'service', 'service_name_at_time', 'price_at_time', 'quantity', 'total_price']
        read_only_fields = ['id', 'service_name_at_time', 'price_at_time']
    
    def get_total_price(self, obj):
        return obj.total_price()


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    patient_name = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ['id', 'patient', 'patient_name', 'date_created', 'is_paid', 'items', 'total_amount', 'created_by']
        read_only_fields = ['id', 'date_created', 'items', 'created_by']
    
    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"
    
    def get_total_amount(self, obj):
        return obj.total_amount()


class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Detailed invoice view with patient info"""
    items = InvoiceItemSerializer(many=True, read_only=True)
    patient = PatientSerializer(read_only=True)
    total_amount = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'patient', 'date_created', 'is_paid', 'items', 'total_amount', 'created_by', 'created_by_name']
        read_only_fields = ['id', 'date_created', 'items', 'created_by', 'created_by_name']
    
    def get_total_amount(self, obj):
        return obj.total_amount()

