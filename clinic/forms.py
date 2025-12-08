from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Patient, Service, Invoice

class StaffRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="At least 8 characters, not entirely numeric.",
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match")
        return cleaned_data


class PatientForm(forms.ModelForm):
    """Form for adding new patient to the system"""
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'contact_number', 'email', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
                'required': True
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number (e.g., 09XXXXXXXXX)',
                'type': 'tel'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Address',
                'rows': 3
            }),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'category', 'description', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Name', 'required': True}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price', 'required': True}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['patient', 'is_paid']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

