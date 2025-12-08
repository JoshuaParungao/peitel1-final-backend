from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F
from django.urls import path
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Service, Patient, Invoice, InvoiceItem, StaffProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# --- Service Admin ---
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('category_display', 'name', 'price_display', 'active_status')
    list_filter = ('category', 'active', 'price')
    search_fields = ('name', 'category', 'description')
    ordering = ('category', 'name')
    fieldsets = (
        ('Service Information', {
            'fields': ('category', 'name', 'description', 'price')
        }),
        ('Status', {
            'fields': ('active',)
        }),
    )
    
    def category_display(self, obj):
        category_labels = dict(obj.DENTAL_CATEGORIES)
        return category_labels.get(obj.category, obj.category)
    category_display.short_description = 'Service Type'
    
    def price_display(self, obj):
        return format_html('<strong>₱{:,.2f}</strong>', obj.price)
    price_display.short_description = 'Price'
    
    def active_status(self, obj):
        color = 'green' if obj.active else 'red'
        status = 'Active' if obj.active else 'Inactive'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, status)
    active_status.short_description = 'Status'


# --- Patient Admin ---
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'contact_number', 'email', 'total_invoices', 'total_spent', 'created_by', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'contact_number')
    ordering = ('last_name', 'first_name')
    readonly_fields = ('created_info', 'invoice_history', 'created_by', 'created_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'contact_number', 'created_by', 'created_at')
        }),
        ('Address', {
            'fields': ('address',)
        }),
        ('History', {
            'fields': ('created_info', 'invoice_history'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Patient Name'
    full_name.admin_order_field = 'last_name'
    
    def total_invoices(self, obj):
        count = obj.invoices.count()
        return format_html('<span style="color: blue; font-weight: bold;">{}</span>', count)
    total_invoices.short_description = 'Total Invoices'
    
    def total_spent(self, obj):
        total = sum(inv.total_amount() for inv in obj.invoices.all())
        # Ensure numeric formatting is applied to a native Python number/string
        try:
            formatted = f"₱{float(total):,.2f}"
        except Exception:
            # Fallback: coerce to string if Decimal/other formatting fails
            formatted = f"₱{total}"
        return format_html('<span style="color: darkgreen; font-weight: bold;">{}</span>', formatted)
    total_spent.short_description = 'Total Spent'
    
    def created_info(self, obj):
        invoices = obj.invoices.all()
        if invoices.exists():
            first_invoice = invoices.first()
            return first_invoice.date_created
        return "No invoices yet"
    created_info.short_description = 'First Service Date'
    
    def invoice_history(self, obj):
        invoices = obj.invoices.all()[:5]
        if not invoices:
            return "No invoices"
        html = '<table style="width: 100%; border-collapse: collapse;"><tr><th style="border: 1px solid #ddd; padding: 5px;">Date</th><th style="border: 1px solid #ddd; padding: 5px;">Amount</th><th style="border: 1px solid #ddd; padding: 5px;">Status</th></tr>'
        for inv in invoices:
            status = '✓ Paid' if inv.is_paid else '⏳ Pending'
            html += f'<tr><td style="border: 1px solid #ddd; padding: 5px;">{inv.date_created.strftime("%Y-%m-%d")}</td><td style="border: 1px solid #ddd; padding: 5px;">₱{inv.total_amount():,.2f}</td><td style="border: 1px solid #ddd; padding: 5px;">{status}</td></tr>'
        html += '</table>'
        return format_html(html)
    invoice_history.short_description = 'Recent Invoices (Last 5)'


# --- Invoice Item Inline ---
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('service', 'service_name_at_time', 'price_at_time', 'quantity', 'item_total')
    readonly_fields = ('service_name_at_time', 'price_at_time', 'item_total')
    
    def item_total(self, obj):
        if obj.pk:
            try:
                amount = float(obj.total_price())
                formatted = f"₱{amount:,.2f}"
            except Exception:
                formatted = f"₱{obj.total_price()}"
            return format_html('<strong>{}</strong>', formatted)
        return '₱0.00'
    item_total.short_description = 'Total'


# --- Invoice Admin ---
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'patient_name', 'date_display', 'payment_status', 'total_amount_display', 'action_buttons')
    list_filter = ('is_paid', 'date_created')
    search_fields = ('patient__first_name', 'patient__last_name', 'id')
    inlines = [InvoiceItemInline]
    date_hierarchy = 'date_created'
    readonly_fields = ('date_created', 'invoice_summary')
    fieldsets = (
        ('Invoice Information', {
            'fields': ('patient', 'date_created', 'is_paid')
        }),
        ('Summary', {
            'fields': ('invoice_summary',)
        }),
    )
    
    def invoice_id(self, obj):
        return format_html('<strong>#{}</strong>', obj.id)
    invoice_id.short_description = 'Invoice #'
    
    def patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'patient__last_name'
    
    def date_display(self, obj):
        return obj.date_created.strftime("%b %d, %Y %I:%M %p")
    date_display.short_description = 'Date'
    date_display.admin_order_field = 'date_created'
    
    def payment_status(self, obj):
        if obj.is_paid:
            return format_html('<span style="color: green; font-weight: bold;">✓ PAID</span>')
        return format_html('<span style="color: red; font-weight: bold;">⏳ PENDING</span>')
    payment_status.short_description = 'Status'
    payment_status.admin_order_field = 'is_paid'
    
    def total_amount_display(self, obj):
        amount = obj.total_amount()
        try:
            formatted = f"₱{float(amount):,.2f}"
        except Exception:
            formatted = f"₱{amount}"
        return format_html('<span style="color: darkgreen; font-weight: bold; font-size: 14px;">{}</span>', formatted)
    total_amount_display.short_description = 'Total Amount'
    
    def action_buttons(self, obj):
        if obj.is_paid:
            return format_html('<span style="color: green;">Payment Completed</span>')
        return format_html('<span style="background-color: #FFC107; padding: 5px 10px; border-radius: 3px; color: black;">Awaiting Payment</span>')
    action_buttons.short_description = 'Action'
    
    def invoice_summary(self, obj):
        items = obj.items.all()
        if not items:
            return "No items in this invoice"
        
        html = '<div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">'
        html += '<h3>Invoice Summary</h3>'
        html += '<table style="width: 100%; border-collapse: collapse;"><tr><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Service</th><th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Qty</th><th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Unit Price</th><th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Total</th></tr>'
        
        subtotal = 0
        for item in items:
            item_total = item.total_price()
            subtotal += item_total
            html += f'<tr><td style="border: 1px solid #ddd; padding: 8px;">{item.service_name_at_time}</td><td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{item.quantity}</td><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">₱{item.price_at_time:,.2f}</td><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">₱{item_total:,.2f}</td></tr>'
        
        html += f'<tr style="background-color: #e3f2fd; font-weight: bold;"><td colspan="3" style="border: 1px solid #ddd; padding: 8px; text-align: right;">SUBTOTAL:</td><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">₱{subtotal:,.2f}</td></tr>'
        html += f'<tr style="background-color: #fff3e0; font-weight: bold; font-size: 16px;"><td colspan="3" style="border: 1px solid #ddd; padding: 8px; text-align: right;">TOTAL AMOUNT:</td><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">₱{subtotal:,.2f}</td></tr>'
        html += '</table>'
        html += '</div>'
        
        return format_html(html)
    invoice_summary.short_description = 'Invoice Details'


# --- Custom User Admin ---
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'full_name', 'email', 'staff_position', 'user_role', 'approval_status', 'last_login_display')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'last_login')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    actions = ['approve_staff', 'reject_staff']
    
    def full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else "(No name set)"
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'first_name'
    
    def staff_position(self, obj):
        """Display staff position from StaffProfile"""
        if hasattr(obj, 'staff_profile'):
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
                obj.staff_profile.get_position_display()
            )
        return format_html('<span style="color: gray;">N/A</span>')
    staff_position.short_description = 'Position'
    
    def user_role(self, obj):
        if obj.is_superuser:
            return format_html('<span style="background-color: red; color: white; padding: 3px 8px; border-radius: 3px;">Admin</span>')
        elif obj.is_staff:
            return format_html('<span style="background-color: blue; color: white; padding: 3px 8px; border-radius: 3px;">Staff</span>')
        return format_html('<span style="background-color: gray; color: white; padding: 3px 8px; border-radius: 3px;">User</span>')
    user_role.short_description = 'Role'
    
    def approval_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Approved</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">⏳ Pending Approval</span>')
    approval_status.short_description = 'Status'
    approval_status.admin_order_field = 'is_active'
    
    def last_login_display(self, obj):
        if obj.last_login:
            return obj.last_login.strftime("%b %d, %Y %I:%M %p")
        return "Never"
    last_login_display.short_description = 'Last Login'
    last_login_display.admin_order_field = 'last_login'
    
    def approve_staff(self, request, queryset):
        """Approve selected staff members"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} staff member(s) approved successfully.')
    approve_staff.short_description = "✓ Approve Selected Staff"
    
    def reject_staff(self, request, queryset):
        """Reject/Deactivate selected staff members"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} staff member(s) rejected/deactivated.')
    reject_staff.short_description = "✗ Reject/Deactivate Selected Staff"


# --- StaffProfile Admin ---
@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'position_display', 'patients_added', 'invoices_created', 'created_at')
    list_filter = ('position', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'created_at', 'activity_summary')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'created_at')
        }),
        ('Position', {
            'fields': ('position',)
        }),
        ('Activity Summary', {
            'fields': ('activity_summary',),
            'classes': ('wide',)
        }),
    )
    
    def username(self, obj):
        return obj.user.username
    username.short_description = 'Username'
    username.admin_order_field = 'user__username'
    
    def full_name(self, obj):
        name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return name if name else "(No name set)"
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'user__first_name'
    
    def position_display(self, obj):
        return format_html(
            '<span style="background-color: #2196F3; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            obj.get_position_display()
        )
    position_display.short_description = 'Position'
    position_display.admin_order_field = 'position'
    
    def patients_added(self, obj):
        """Count patients added by this staff member"""
        count = Patient.objects.filter(created_by=obj.user).count()
        return format_html(
            '<span style="background-color: #4CAF50; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            count
        )
    patients_added.short_description = 'Patients Added'
    
    def invoices_created(self, obj):
        """Count invoices created by this staff member (via patients they added or directly)"""
        # Get invoices for patients added by this staff member
        patient_ids = Patient.objects.filter(created_by=obj.user).values_list('id', flat=True)
        count = Invoice.objects.filter(patient_id__in=patient_ids).count()
        return format_html(
            '<span style="background-color: #2196F3; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            count
        )
    invoices_created.short_description = 'Invoices (via patients)'
    
    def activity_summary(self, obj):
        """Show detailed activity for this staff member"""
        # Get all patients added by this user
        patients = Patient.objects.filter(created_by=obj.user).order_by('-created_at')
        
        # Get all invoices for those patients
        patient_ids = patients.values_list('id', flat=True)
        invoices = Invoice.objects.filter(patient_id__in=patient_ids).order_by('-date_created')
        
        # Calculate totals
        total_invoices = invoices.count()
        total_amount = invoices.aggregate(Sum('items__price_at_time'))['items__price_at_time__sum'] or 0
        paid_invoices = invoices.filter(is_paid=True).count()
        pending_invoices = invoices.filter(is_paid=False).count()
        
        html = '<div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">'
        html += '<h3>Activity Summary</h3>'
        
        # Summary Stats
        html += '<table style="width: 100%; margin-bottom: 15px; border-collapse: collapse;">'
        html += '<tr style="background-color: #e3f2fd;">'
        html += f'<td style="border: 1px solid #ddd; padding: 8px;"><strong>Patients Added:</strong></td><td style="border: 1px solid #ddd; padding: 8px;">{patients.count()}</td>'
        html += f'<td style="border: 1px solid #ddd; padding: 8px;"><strong>Total Invoices:</strong></td><td style="border: 1px solid #ddd; padding: 8px;">{total_invoices}</td>'
        html += '</tr>'
        html += '<tr>'
        html += f'<td style="border: 1px solid #ddd; padding: 8px;"><strong>Total Revenue:</strong></td><td style="border: 1px solid #ddd; padding: 8px; color: green; font-weight: bold;">₱{float(total_amount):,.2f}</td>'
        html += f'<td style="border: 1px solid #ddd; padding: 8px;"><strong>Paid/Pending:</strong></td><td style="border: 1px solid #ddd; padding: 8px;"><span style="color: green;">✓ {paid_invoices}</span> / <span style="color: orange;">⏳ {pending_invoices}</span></td>'
        html += '</tr>'
        html += '</table>'
        
        # Recent Patients
        if patients.exists():
            html += '<h4>Recent Patients Added (Last 10):</h4>'
            html += '<table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">'
            html += '<tr style="background-color: #fff3e0;"><th style="border: 1px solid #ddd; padding: 8px;">Patient Name</th><th style="border: 1px solid #ddd; padding: 8px;">Added Date</th><th style="border: 1px solid #ddd; padding: 8px;">Invoices</th><th style="border: 1px solid #ddd; padding: 8px;">Total Spent</th></tr>'
            
            for patient in patients[:10]:
                patient_invoices = patient.invoices.all()
                patient_total = sum(inv.total_amount() for inv in patient_invoices)
                date_added = patient.created_at.strftime("%b %d, %Y")
                html += f'<tr><td style="border: 1px solid #ddd; padding: 8px;">{patient.first_name} {patient.last_name}</td><td style="border: 1px solid #ddd; padding: 8px;">{date_added}</td><td style="border: 1px solid #ddd; padding: 8px;">{patient_invoices.count()}</td><td style="border: 1px solid #ddd; padding: 8px; color: darkgreen; font-weight: bold;">₱{float(patient_total):,.2f}</td></tr>'
            
            html += '</table>'
        else:
            html += '<p style="color: #999;">No patients added yet.</p>'
        
        # Recent Invoices
        if invoices.exists():
            html += '<h4>Recent Invoices (Last 10):</h4>'
            html += '<table style="width: 100%; border-collapse: collapse;">'
            html += '<tr style="background-color: #e8f5e9;"><th style="border: 1px solid #ddd; padding: 8px;">Invoice #</th><th style="border: 1px solid #ddd; padding: 8px;">Patient</th><th style="border: 1px solid #ddd; padding: 8px;">Date</th><th style="border: 1px solid #ddd; padding: 8px;">Amount</th><th style="border: 1px solid #ddd; padding: 8px;">Status</th></tr>'
            
            for invoice in invoices[:10]:
                amount = invoice.total_amount()
                date_created = invoice.date_created.strftime("%b %d, %Y")
                status = '<span style="color: green; font-weight: bold;">✓ PAID</span>' if invoice.is_paid else '<span style="color: orange; font-weight: bold;">⏳ PENDING</span>'
                html += f'<tr><td style="border: 1px solid #ddd; padding: 8px;">#{invoice.id}</td><td style="border: 1px solid #ddd; padding: 8px;">{invoice.patient.first_name} {invoice.patient.last_name}</td><td style="border: 1px solid #ddd; padding: 8px;">{date_created}</td><td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">₱{float(amount):,.2f}</td><td style="border: 1px solid #ddd; padding: 8px;">{status}</td></tr>'
            
            html += '</table>'
        else:
            html += '<p style="color: #999;">No invoices created yet.</p>'
        
        html += '</div>'
        return format_html(html)
    activity_summary.short_description = 'Staff Activity'


# Unregister default User admin and register custom
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# --- Custom Admin Site with Sales Dashboard ---
class SalesAdminSite(admin.AdminSite):
    site_header = "Dental Clinic Administration"
    site_title = "Clinic Admin"
    index_title = "Dashboard"
    
    def index(self, request, extra_context=None):
        """Override index to add sales data"""
        now = timezone.now()
        today = now.date()
        
        # Calculate sales totals
        today_invoices = Invoice.objects.filter(date_created__date=today)
        today_total = today_invoices.aggregate(Sum('items__price_at_time'))['items__price_at_time__sum'] or 0
        
        week_start = now - timedelta(days=7)
        week_invoices = Invoice.objects.filter(date_created__gte=week_start)
        week_total = week_invoices.aggregate(Sum('items__price_at_time'))['items__price_at_time__sum'] or 0
        
        month_invoices = Invoice.objects.filter(date_created__year=now.year, date_created__month=now.month)
        month_total = month_invoices.aggregate(Sum('items__price_at_time'))['items__price_at_time__sum'] or 0
        
        year_invoices = Invoice.objects.filter(date_created__year=now.year)
        year_total = year_invoices.aggregate(Sum('items__price_at_time'))['items__price_at_time__sum'] or 0
        
        # Count stats
        total_patients = Patient.objects.count()
        total_invoices = Invoice.objects.count()
        pending_invoices = Invoice.objects.filter(is_paid=False).count()
        paid_invoices = Invoice.objects.filter(is_paid=True).count()
        
        extra_context = extra_context or {}
        extra_context.update({
            'sales_today': float(today_total),
            'sales_week': float(week_total),
            'sales_month': float(month_total),
            'sales_year': float(year_total),
            'total_patients': total_patients,
            'total_invoices': total_invoices,
            'pending_invoices': pending_invoices,
            'paid_invoices': paid_invoices,
        })
        
        return super().index(request, extra_context)


# Create and register the custom admin site
custom_admin_site = SalesAdminSite(name='custom_admin')

# Re-register the models with the custom admin site
custom_admin_site.register(Service, ServiceAdmin)
custom_admin_site.register(Patient, PatientAdmin)
custom_admin_site.register(Invoice, InvoiceAdmin)
custom_admin_site.register(StaffProfile, StaffProfileAdmin)
custom_admin_site.register(User, CustomUserAdmin)
