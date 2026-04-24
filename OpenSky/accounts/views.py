from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from teams.models import AuditLog

User = get_user_model()
is_staff = lambda u: u.is_staff

# Mirrors _log() in teams/views.py — both write to the shared AuditLog model
def _log(action, obj_type, obj_name, user, details=''):
    AuditLog.objects.create(
        action=action,
        object_type=obj_type,
        object_name=obj_name,
        performed_by=getattr(user, 'username', str(user)),
        details=details,
    )


def user_login(request):
    # Redirect already-authenticated users straight to their dashboard
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'dashboard')

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember_me')

        # authenticate() calls EmailBackend first (looks up by email, not username)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Prevent staff from using the regular login page
            if user.is_staff:
                messages.error(request, 'Please use the Admin Login page.')
                return redirect('admin_login')
            login(request, user)
            if not remember:
                request.session.set_expiry(0)  # Session ends when browser closes
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'registration/user_login.html')


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        admin_id = request.POST.get('admin_id', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember_me')

        # Admin ID is stored as username for staff users
        try:
            user_obj = User.objects.get(username=admin_id, is_staff=True)
            user = authenticate(request, username=user_obj.email, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None and user.is_staff:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid Admin ID or password.')

    return render(request, 'registration/admin_login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not email:
            messages.error(request, 'Email address is required.')
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email already exists.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            # Use email as username to avoid unique constraint issues
            username = email.split('@')[0][:150]
            # Ensure username is unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            new_user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
            )
            _log('create', 'User', username, new_user, f'Self-registered with email {email}')
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')

    return render(request, 'registration/signup.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def forgot_password_view(request):
    sent = False
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            sent = True
            messages.info(request, 'If that email exists, a password reset link will be sent.')
    return render(request, 'registration/forgot_password.html', {'sent': sent})


@login_required
def profile_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip().lower()
        if not email:
            messages.error(request, 'Email is required.')
        elif User.objects.filter(email__iexact=email).exclude(pk=request.user.pk).exists():
            messages.error(request, 'That email is already in use.')
        else:
            request.user.first_name = first_name
            request.user.last_name  = last_name
            request.user.email      = email
            request.user.save()
            _log('update', 'User', request.user.username, request.user, 'Profile updated')
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    return render(request, 'accounts/profile.html')


@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        current = request.POST.get('current_password', '')
        new1    = request.POST.get('new_password1', '')
        new2    = request.POST.get('new_password2', '')
        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
        elif new1 != new2:
            messages.error(request, 'New passwords do not match.')
        elif len(new1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            request.user.set_password(new1)
            request.user.save()
            # Keeps the user logged in after password change by updating the session hash
            update_session_auth_hash(request, request.user)
            _log('update', 'User', request.user.username, request.user, 'Password changed')
            messages.success(request, 'Password changed successfully.')
            return redirect('settings')
    return render(request, 'accounts/change_password.html')


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/admin_users.html', {'users': users})


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_user_toggle_staff(request, user_id):
    if request.method == 'POST':
        target = get_object_or_404(User, pk=user_id)
        if target == request.user:
            messages.error(request, 'You cannot change your own admin status.')
        else:
            target.is_staff = not target.is_staff
            target.save()
            action_label = 'Admin granted' if target.is_staff else 'Admin revoked'
            _log('update', 'User', target.username, request.user, f'{action_label} for {target.email}')
            status = 'granted admin' if target.is_staff else 'revoked admin from'
            messages.success(request, f'Successfully {status} {target.get_full_name() or target.username}.')
    return redirect('admin_users')


@user_passes_test(is_staff, login_url='/accounts/login/')
def admin_user_delete(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        if target == request.user:
            messages.error(request, 'You cannot delete your own account.')
        else:
            name = target.get_full_name() or target.username
            uname = target.username
            target.delete()
            _log('delete', 'User', uname, request.user, f'User account deleted ({name})')
            messages.success(request, f'User {name} deleted.')
        return redirect('admin_users')
    return render(request, 'accounts/admin_user_confirm_delete.html', {'target': target})
