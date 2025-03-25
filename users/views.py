from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserLoginForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")  # Redirect if already logged in

    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")  # Redirect to dashboard
        else:
            messages.error(request, "Invalid login credentials")

    else:
        form = UserLoginForm()

    return render(request, "register/login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")
