from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, FormView, TemplateView
from django.urls import reverse_lazy

from .models import CustomUser
from .forms import UserRegisterForm, UserLoginForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_router')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome to AgriConnect, {user.first_name or user.username}! You are registered as {user.get_role_display()}."
            )
            return redirect('dashboard_router')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        initial_role = request.GET.get('role', CustomUser.Role.CONSUMER)
        form = UserRegisterForm(initial={'role': initial_role})

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_router')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard_router')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def dashboard_router_view(request):
    """
    Intelligent role-based router that forwards each user to their role-specific hub.
    """
    user = request.user
    if user.is_facilitator:
        return redirect('facilitator_dashboard')
    elif user.is_farmer:
        return redirect('farmer_dashboard')
    elif user.is_consumer:
        return redirect('marketplace_catalog')
    elif user.is_delivery:
        return redirect('dispatch_dashboard')
    
    return render(request, 'accounts/dashboard_hub.html', {'user': user})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


def quick_switch_user_view(request, username):
    """
    Helper view for SIH evaluation / rapid testing:
    Allows instant persona switching between demo accounts with a single click.
    """
    try:
        user = CustomUser.objects.get(username=username)
        login(request, user)
        messages.success(request, f"Switched to {user.get_role_display()} persona ({user.username}).")
    except CustomUser.DoesNotExist:
        messages.error(request, f"Demo account '{username}' does not exist. Run 'python manage.py seed_phase1'.")
    return redirect('dashboard_router')
