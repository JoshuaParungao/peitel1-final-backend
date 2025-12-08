from django.contrib.auth.views import LoginView
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render
from django.views import View
from django.conf import settings
from django.contrib.auth.models import User
from .forms import StaffRegistrationForm
from .models import StaffProfile


class FrontendLoginView(LoginView):
    template_name = 'clinic/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to dashboard after successful login"""
        return '/clinic/'

    def form_valid(self, form):
        # Only allow Django superusers to log in via the clinic frontend.
        user = form.get_user()
        if not user.is_superuser:
            form.add_error(None, 'Only superuser accounts may sign in to the admin dashboard here.')
            return self.form_invalid(form)

        response = super().form_valid(form)
        # Mark that the user explicitly logged in via frontend
        self.request.session['frontend_authenticated'] = True
        self.request.session.save()
        return response


class FrontendRegistrationView(View):
    """Registration view for new staff members"""
    
    def get(self, request):
        form = StaffRegistrationForm()
        return render(request, 'clinic/register.html', {'form': form})
    
    def post(self, request):
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            # Create the user with is_staff=True but not a superuser
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password'],
                is_staff=True,  # Mark as staff so they can access admin
                is_active=False,  # Require approval by admin
            )
            
            # Create staff profile for tracking
            StaffProfile.objects.create(
                user=user,
                position='other',
                approved=False,
            )
            
            # Mark registration in session so the approval page can show a confirmation
            try:
                request.session['registered_username'] = user.username
                request.session.modified = True
            except Exception:
                pass

            # Redirect to staff approval page
            return redirect('clinic:staff_approval')
        
        return render(request, 'clinic/register.html', {'form': form})


class FrontendLogoutView(View):
    """A simple logout handler that clears the frontend flag and redirects
    explicitly to the landing page.
    """

    def get(self, request, *args, **kwargs):
        request.session.pop('frontend_authenticated', None)
        auth_logout(request)
        return redirect('landing')

    def post(self, request, *args, **kwargs):
        # Allow logout via POST as well
        request.session.pop('frontend_authenticated', None)
        auth_logout(request)
        return redirect('landing')

