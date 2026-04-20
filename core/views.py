import re

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from item.models import Category, Item


def index(request):
    categories = Category.objects.all()
    selected_category = request.GET.get("category")
    search_query = request.GET.get("q", "").strip()
    selected_category_obj = None

    items_queryset = Item.objects.select_related("category", "reported_by").filter(is_public=True)
    if selected_category:
        try:
            selected_category_id = int(selected_category)
            selected_category_obj = categories.filter(id=selected_category_id).first()
            if selected_category_obj:
                items_queryset = items_queryset.filter(category_id=selected_category_id)
            else:
                selected_category = None
        except (TypeError, ValueError):
            selected_category = None

    if search_query:
        items_queryset = items_queryset.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(location__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(status__icontains=search_query)
        )

    recent_items = items_queryset[:12]
    lost_items = items_queryset.filter(status=Item.Status.LOST)[:6]
    found_items = items_queryset.filter(status=Item.Status.FOUND)[:6]

    context = {
        "categories": categories,
        "recent_items": recent_items,
        "lost_items": lost_items,
        "found_items": found_items,
        "selected_category": selected_category,
        "selected_category_obj": selected_category_obj,
        "search_query": search_query,
        "item_count": items_queryset.count(),
        "category_count": categories.count(),
    }
    return render(request, 'core/index.html', context)

def contact(request):
    return render(request, 'core/contact.html')


@ensure_csrf_cookie
def login(request):
    error_message = None
    show_signup_prompt = False
    matric_pattern = r"^BU\d{2}[A-Z]{3}\d{4}$"

    if request.method == "POST":
        entered_username = request.POST.get("matric_number", "").strip()
        password = request.POST.get("password", "")
        matric_number = entered_username.upper()

        admin_username_entry = entered_username.lower() == "admin"
        superuser_username_entry = User.objects.filter(username=entered_username, is_superuser=True).exists()

        if admin_username_entry or superuser_username_entry:
            user = authenticate(request, username=entered_username, password=password)
            if user is not None and (user.is_staff or user.is_superuser):
                auth_login(request, user)
                return redirect("/admin/")
            error_message = "Invalid admin username or password."
            return render(request, "core/login.html", {"error_message": error_message, "show_signup_prompt": show_signup_prompt})

        if not re.fullmatch(matric_pattern, matric_number):
            error_message = "Matric number must follow this format: BU23CSC1109."
            return render(request, "core/login.html", {"error_message": error_message, "show_signup_prompt": show_signup_prompt})

        if len(password) < 4:
            error_message = "Password must be at least 4 characters."
            return render(request, "core/login.html", {"error_message": error_message, "show_signup_prompt": show_signup_prompt})

        if not User.objects.filter(username=matric_number).exists():
            error_message = "You do not have an account yet?"
            show_signup_prompt = True
            return render(request, "core/login.html", {"error_message": error_message, "show_signup_prompt": show_signup_prompt})

        user = authenticate(request, username=matric_number, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("index")

        error_message = "Invalid matric number or password."

    return render(request, "core/login.html", {"error_message": error_message, "show_signup_prompt": show_signup_prompt})

@ensure_csrf_cookie
def signup(request):
    error_message = None
    matric_pattern = r"^BU\d{2}[A-Z]{3}\d{4}$"

    if request.method == "POST":
        matric_number = request.POST.get("matric_number", "").strip().upper()
        password = request.POST.get("password", "")

        if not re.fullmatch(matric_pattern, matric_number):
            error_message = "Matric number must follow this format: BU20CSC0000."
            return render(request, "core/signup.html", {"error_message": error_message})

        if len(password) < 4:
            error_message = "Password must be at least 4 characters."
            return render(request, "core/signup.html", {"error_message": error_message})

        if User.objects.filter(username=matric_number).exists():
            error_message = "This matric number is already registered."
            return render(request, "core/signup.html", {"error_message": error_message})

        password_already_used = any(user.check_password(password) for user in User.objects.all())
        if password_already_used:
            error_message = "This password has already been used. Choose a different password."
            return render(request, "core/signup.html", {"error_message": error_message})

        user = User.objects.create_user(username=matric_number, password=password)
        auth_login(request, user)
        return redirect("index")

    return render(request, "core/signup.html")


def logout_view(request):
    auth_logout(request)
    return redirect("login")
