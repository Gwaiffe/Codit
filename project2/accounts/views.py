from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from . import forms
# Create your views here.


def register(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display blank registration form.
        form = UserCreationForm()
    else:
        # Process completed form.
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
    # Log the user in and then redirect to home page.
            login(request, new_user)
            return redirect('blog:home_page')
    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'Registration/register.html', context)


@login_required
def edit_profile(request):
    if request.method != 'POST':
        form = forms.ProfileForm(instance=request.user.profile)
    else:
        form = forms.ProfileForm(
            request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    context = {'form': form}
    return render(request, 'edit_profile.html', context)
