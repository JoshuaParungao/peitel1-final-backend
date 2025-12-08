# clinic/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class StaffProfile(models.Model):
    """Extended profile for staff users with position/role information"""
    POSITIONS = [
        ('dentist', 'Dentist'),
        ('hygienist', 'Dental Hygienist'),
        ('assistant', 'Dental Assistant'),
        ('receptionist', 'Receptionist'),
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    position = models.CharField(max_length=50, choices=POSITIONS, default='other')
    created_at = models.DateTimeField(default=timezone.now)
    # New fields for approval workflow and soft-delete (archive)
    approved = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.get_position_display()}"


class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_patients')
    created_at = models.DateTimeField(default=timezone.now)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Service(models.Model):
    DENTAL_CATEGORIES = [
        ("CHECKUP", "Dental Check-up / Consultation"),
        ("CLEANING", "Oral Prophylaxis / Cleaning"),
        ("FLUORIDE", "Fluoride Treatment"),
        ("SEALANTS", "Sealants"),
        ("FILLING", "Tooth Filling / Restoration"),
        ("CROWN", "Crown and Bridge"),
        ("VENEERS", "Veneers"),
        ("ROOTCANAL", "Root Canal Treatment"),
        ("EXTRACTION", "Tooth Extraction"),
        ("SURGICAL_EXTRACTION", "Surgical Extraction"),
        ("WISDOM_TOOTH", "Wisdom Tooth Removal"),
        ("BRACES_METAL", "Braces - Metal"),
        ("BRACES_CERAMIC", "Braces - Ceramic"),
        ("CLEAR_ALIGNERS", "Clear Aligners / Invisalign"),
        ("DENTURES_PARTIAL", "Partial Dentures"),
        ("DENTURES_FULL", "Full Dentures"),
        ("IMPLANT", "Dental Implants"),
        ("SCALING_ROOTPLANING", "Scaling and Root Planing"),
        ("GUM_SURGERY", "Gum Surgery"),
        ("TEETH_WHITENING", "Teeth Whitening"),
        ("SMILE_MAKEOVER", "Smile Makeover"),
        ("DENTAL_XRAY", "Dental X-ray"),
        ("PANORAMIC_XRAY", "Panoramic X-ray"),
        ("PEDIATRIC_CHECKUP", "Child Check-up"),
        ("PEDIATRIC_FLUORIDE", "Fluoride for Kids"),
        ("PULPOTOMY", "Pulpotomy / Pediatric Filling"),
        ("MEDICAL_CERTIFICATE", "Medical Certificate"),
    ]

    DEFAULT_PRICES = {
        "CHECKUP": 500, "CLEANING": 800, "FLUORIDE": 600, "SEALANTS": 1000,
        "FILLING": 1200, "CROWN": 8000, "VENEERS": 12000, "ROOTCANAL": 5000,
        "EXTRACTION": 1500, "SURGICAL_EXTRACTION": 3000, "WISDOM_TOOTH": 3500,
        "BRACES_METAL": 25000, "BRACES_CERAMIC": 40000, "CLEAR_ALIGNERS": 80000,
        "DENTURES_PARTIAL": 15000, "DENTURES_FULL": 25000, "IMPLANT": 80000,
        "SCALING_ROOTPLANING": 2000, "GUM_SURGERY": 7000, "TEETH_WHITENING": 5000,
        "SMILE_MAKEOVER": 15000, "DENTAL_XRAY": 800, "PANORAMIC_XRAY": 1500,
        "PEDIATRIC_CHECKUP": 400, "PEDIATRIC_FLUORIDE": 500, "PULPOTOMY": 2000,
        "MEDICAL_CERTIFICATE": 300
    }

    category = models.CharField(max_length=50, choices=DENTAL_CATEGORIES, default="CHECKUP")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.DEFAULT_PRICES.get(self.category, 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} — ₱{self.price:,.2f}"


class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="invoices")
    date_created = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    # Track which staff user created the invoice (nullable for legacy data)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_invoices')
    # Soft-delete flag for archiving invoices instead of hard delete
    is_archived = models.BooleanField(default=False)

    def total_amount(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Invoice #{self.id} - {self.patient}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_name_at_time = models.CharField(max_length=150)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.price_at_time = self.service.price
            self.service_name_at_time = self.service.name
        super().save(*args, **kwargs)

    def total_price(self):
        return self.price_at_time * self.quantity
