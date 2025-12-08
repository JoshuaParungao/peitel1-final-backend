from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import io
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Patient, Service, Invoice
from .forms import PatientForm, ServiceForm

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')(view_func)

# 1. Authentication
def login_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('clinic:dashboard')
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            auth_login(request, user)
            return redirect('clinic:dashboard')
        return render(request, 'clinic/login.html', {'error': 'Invalid credentials or not superuser'})
    return render(request, 'clinic/login.html')

@superuser_required
def logout_view(request):
    auth_logout(request)
    return redirect('login')

# 2. Dashboard
@superuser_required
def dashboard(request):
    context = {
        'total_patients': Patient.objects.filter(is_archived=False).count(),
        'total_services': Service.objects.filter(is_archived=False).count(),
        'total_invoices': Invoice.objects.filter(is_archived=False).count(),
        'total_staff': User.objects.filter(is_staff=True, is_active=True).count(),
    }
    return render(request, 'clinic/dashboard.html', context)

# 3. Patients Module
@superuser_required
def patients_list(request):
    patients = Patient.objects.filter(is_archived=False)
    return render(request, 'clinic/patient_list.html', {'patients': patients, 'back_url': reverse('clinic:dashboard')})

@superuser_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'clinic/patient_detail.html', {'patient': patient, 'back_url': reverse('clinic:dashboard')})

@superuser_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clinic:patients_list')
    else:
        form = PatientForm()
    return render(request, 'clinic/patient_form.html', {'form': form, 'back_url': reverse('clinic:dashboard')})

@superuser_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('clinic:patients_list')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'clinic/patient_form.html', {'form': form, 'back_url': reverse('clinic:dashboard')})

@superuser_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    patient.is_archived = True
    patient.save()
    return redirect('clinic:patients_list')

# 4. Services Module
@superuser_required
def services_list(request):
    services = Service.objects.filter(is_archived=False)
    return render(request, 'clinic/service_list.html', {'services': services, 'back_url': reverse('clinic:dashboard')})

@superuser_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clinic:services_list')
    else:
        form = ServiceForm()
    return render(request, 'clinic/service_form.html', {'form': form, 'back_url': reverse('clinic:dashboard')})

@superuser_required
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('clinic:services_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'clinic/service_form.html', {'form': form, 'back_url': reverse('clinic:dashboard')})

@superuser_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.is_archived = True
    service.save()
    return redirect('clinic:services_list')

# 5. Invoices Module
@superuser_required
def invoices_list(request):
    invoices = Invoice.objects.filter(is_archived=False)
    return render(request, 'clinic/invoice_list.html', {'invoices': invoices, 'back_url': reverse('clinic:dashboard')})

@superuser_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'clinic/invoice_detail.html', {'invoice': invoice, 'back_url': reverse('clinic:dashboard')})

@superuser_required
def invoice_create(request):
    if request.method == 'POST':
        return redirect('clinic:invoices_list')
    return render(request, 'clinic/invoice_form.html', {'back_url': reverse('clinic:dashboard')})

@superuser_required
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        return redirect('clinic:invoices_list')
    return render(request, 'clinic/invoice_form.html', {'invoice': invoice, 'back_url': reverse('clinic:dashboard')})

@superuser_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.is_archived = True
    invoice.save()
    return redirect('clinic:invoices_list')


@superuser_required
def invoice_pdf(request, pk):
    """Generate a PDF for a single invoice (download)."""
    invoice = get_object_or_404(Invoice, pk=pk)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    x = 40
    y = height - 40
    p.setFont('Helvetica-Bold', 16)
    p.drawString(x, y, f"Invoice #{invoice.pk}")
    p.setFont('Helvetica', 10)
    y -= 24
    p.drawString(x, y, f"Patient: {invoice.patient.first_name} {invoice.patient.last_name}")
    y -= 14
    p.drawString(x, y, f"Date: {invoice.date_created.strftime('%Y-%m-%d %H:%M')}")
    y -= 20

    # Table header
    p.setFont('Helvetica-Bold', 11)
    p.drawString(x, y, 'Item')
    p.drawString(x+260, y, 'Price')
    p.drawString(x+340, y, 'Qty')
    p.drawString(x+400, y, 'Total')
    y -= 14
    p.setFont('Helvetica', 10)

    total = 0
    for item in invoice.items.all():
        if y < 80:
            p.showPage()
            y = height - 40
        p.drawString(x, y, item.service_name_at_time)
        p.drawRightString(x+320, y, f"₱{float(item.price_at_time):,.2f}")
        p.drawRightString(x+390, y, str(item.quantity))
        line_total = float(item.price_at_time) * item.quantity
        p.drawRightString(x+480, y, f"₱{line_total:,.2f}")
        total += line_total
        y -= 14

    y -= 8
    p.setFont('Helvetica-Bold', 12)
    p.drawString(x, y, f"Total: ₱{total:,.2f}")

    p.showPage()
    p.save()
    buffer.seek(0)
    resp = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="invoice_{invoice.pk}.pdf"'
    return resp


@superuser_required
def sales_summary_csv(request):
    """Export all invoices (not archived) as CSV with a summary row."""
    invoices = Invoice.objects.filter(is_archived=False).order_by('date_created')
    total_sales = 0
    total_count = invoices.count()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    # header
    writer.writerow(['Invoice ID', 'Patient', 'Date', 'Is Paid', 'Created By', 'Total Amount'])
    for inv in invoices:
        amount = sum(float(it.price_at_time) * it.quantity for it in inv.items.all())
        total_sales += amount
        writer.writerow([inv.pk, f"{inv.patient.first_name} {inv.patient.last_name}", inv.date_created.strftime('%Y-%m-%d %H:%M'), 'Yes' if inv.is_paid else 'No', (inv.created_by.get_full_name() if inv.created_by else ''), f"{amount:.2f}"])

    # summary row
    writer.writerow([])
    writer.writerow(['TOTAL_INVOICES', total_count])
    writer.writerow(['TOTAL_SALES', f"{total_sales:.2f}"])

    resp = HttpResponse(buffer.getvalue(), content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename="sales_summary.csv"'
    return resp


@superuser_required
def sales_summary_pdf(request):
    """Generate a PDF summarizing sales (list + totals)."""
    invoices = Invoice.objects.filter(is_archived=False).order_by('date_created')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x = 40
    y = height - 40
    p.setFont('Helvetica-Bold', 16)
    p.drawString(x, y, 'Sales Summary')
    y -= 28
    p.setFont('Helvetica-Bold', 11)
    p.drawString(x, y, 'Invoice')
    p.drawString(x+100, y, 'Patient')
    p.drawString(x+300, y, 'Date')
    p.drawString(x+420, y, 'Total')
    y -= 14
    p.setFont('Helvetica', 10)
    total_sales = 0
    for inv in invoices:
        if y < 80:
            p.showPage()
            y = height - 40
        amount = sum(float(it.price_at_time) * it.quantity for it in inv.items.all())
        total_sales += amount
        p.drawString(x, y, str(inv.pk))
        p.drawString(x+100, y, f"{inv.patient.first_name} {inv.patient.last_name}")
        p.drawString(x+300, y, inv.date_created.strftime('%Y-%m-%d'))
        p.drawRightString(x+500, y, f"₱{amount:,.2f}")
        y -= 14

    y -= 10
    p.setFont('Helvetica-Bold', 12)
    p.drawString(x, y, f"Total Invoices: {invoices.count()}")
    p.drawString(x+220, y, f"Total Sales: ₱{total_sales:,.2f}")
    p.showPage()
    p.save()
    buffer.seek(0)
    resp = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="sales_summary.pdf"'
    return resp

# 6. Archive Module
@superuser_required
def archive(request):
    archived_patients = Patient.objects.filter(is_archived=True)
    archived_services = Service.objects.filter(is_archived=True)
    archived_invoices = Invoice.objects.filter(is_archived=True)
    return render(request, 'clinic/archive.html', {
        'archived_patients': archived_patients,
        'archived_services': archived_services,
        'archived_invoices': archived_invoices,
        'back_url': reverse('clinic:dashboard')
    })

# 7. Staff Approval Module
@superuser_required
def staff_approval(request):
    pending_staff = User.objects.filter(is_staff=True, is_active=False)
    return render(request, 'clinic/staff_approval.html', {'pending_staff': pending_staff, 'back_url': reverse('clinic:dashboard')})

@superuser_required
def approve_staff(request, pk):
    staff = get_object_or_404(User, pk=pk, is_staff=True)
    staff.is_active = True
    staff.save()
    return redirect('clinic:staff_approval')

@superuser_required
def reject_staff(request, pk):
    staff = get_object_or_404(User, pk=pk, is_staff=True)
    staff.delete()
    return redirect('clinic:staff_approval')

# 8. Navigation / Back Button is handled via 'back_url' context in templates

# 9. Logout is handled above
