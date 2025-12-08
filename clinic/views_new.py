from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Patient, Service, Invoice
from .forms import PatientForm, ServiceForm

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='/accounts/login/')(view_func)

# 1. Authentication
def login_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            auth_login(request, user)
            return redirect('dashboard')
        return render(request, 'clinic/login.html', {'error': 'Invalid credentials or not superuser'})
    return render(request, 'clinic/login.html')

@superuser_required
def logout_view(request):
    auth_logout(request)
    return redirect('/accounts/login/')

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
    return render(request, 'clinic/patient_list.html', {'patients': patients})

@superuser_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'clinic/patient_detail.html', {'patient': patient})

@superuser_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patients_list')
    else:
        form = PatientForm()
    return render(request, 'clinic/patient_form.html', {'form': form, 'back_url': reverse('dashboard')})

@superuser_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patients_list')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'clinic/patient_form.html', {'form': form, 'back_url': reverse('dashboard')})

@superuser_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    patient.is_archived = True
    patient.save()
    return redirect('patients_list')

# 4. Services Module
@superuser_required
def services_list(request):
    services = Service.objects.filter(is_archived=False)
    return render(request, 'clinic/service_list.html', {'services': services})

@superuser_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('services_list')
    else:
        form = ServiceForm()
    return render(request, 'clinic/service_form.html', {'form': form, 'back_url': reverse('dashboard')})

@superuser_required
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('services_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'clinic/service_form.html', {'form': form, 'back_url': reverse('dashboard')})

@superuser_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.is_archived = True
    service.save()
    return redirect('services_list')

# 5. Invoices Module
@superuser_required
def invoices_list(request):
    invoices = Invoice.objects.filter(is_archived=False)
    return render(request, 'clinic/invoice_list.html', {'invoices': invoices})

@superuser_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'clinic/invoice_detail.html', {'invoice': invoice})

@superuser_required
def invoice_create(request):
    if request.method == 'POST':
        # Implement invoice creation logic here
        # ...
        return redirect('invoices_list')
    return render(request, 'clinic/invoice_form.html', {'back_url': reverse('dashboard')})

@superuser_required
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        # Implement invoice update logic here
        # ...
        return redirect('invoices_list')
    return render(request, 'clinic/invoice_form.html', {'invoice': invoice, 'back_url': reverse('dashboard')})

@superuser_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.is_archived = True
    invoice.save()
    return redirect('invoices_list')

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
        'back_url': reverse('dashboard')
    })

# 7. Staff Approval Module
@superuser_required
def staff_approval(request):
    pending_staff = User.objects.filter(is_staff=True, is_active=False)
    return render(request, 'clinic/staff_approval.html', {'pending_staff': pending_staff, 'back_url': reverse('dashboard')})

@superuser_required
def approve_staff(request, pk):
    staff = get_object_or_404(User, pk=pk, is_staff=True)
    staff.is_active = True
    staff.save()
    return redirect('staff_approval')

@superuser_required
def reject_staff(request, pk):
    staff = get_object_or_404(User, pk=pk, is_staff=True)
    staff.delete()
    return redirect('staff_approval')

# 8. Navigation / Back Button is handled via 'back_url' context in templates

# 9. Logout is handled above
