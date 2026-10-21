from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Course, Account
from .forms import CourseForm, UserRegistrationForm, UserLoginForm

# Create your views here.
def user_is_teacher(user):
    return user.is_authenticated and user.is_staff

@login_required(login_url='login')
def courses_list(request, user_id=None):
    if user_id:
        if not request.user.is_staff and request.user.id != user_id:
            messages.error(request, "You are not authorized to view this profile.")
            return redirect("home")
        account = get_object_or_404(Account, user=user_id)
        courses = account.enrolled_courses.all()
        return render(request, "account/profile.html", {"registered_courses": courses})
    else:
        query = request.GET.get('q', '')
        selected_credits = request.GET.get('credits', '')
        selected_start_date = request.GET.get('start_date', '')
        selected_end_date = request.GET.get('end_date', '')
        selected_sort = request.GET.get('sort', '')

        courses = Course.objects.all()
        if query:
            courses = courses.filter(
                Q(name__icontains=query) |
                Q(crn__icontains=query) |
                Q(description__icontains=query) |
                Q(instructor__first_name__icontains=query) |
                Q(instructor__last_name__icontains=query) |
                Q(instructor__username__icontains=query)
            )

        if selected_credits:
            courses = courses.filter(credits=selected_credits)

        if selected_start_date:
            courses = courses.filter(start_date=selected_start_date)

        if selected_end_date:
            courses = courses.filter(end_date=selected_end_date)

        sort_fields = {
            'name': 'name',
            'crn': 'crn',
            'instructor': 'instructor__last_name',
        }
        courses = courses.order_by(sort_fields.get(selected_sort, 'name'))

        filter_options = {
            "credits_options": Course.objects.values_list("credits", flat=True).distinct().order_by("credits"),
            "start_date_options": Course.objects.values_list("start_date", flat=True).distinct().order_by("start_date"),
            "end_date_options": Course.objects.values_list("end_date", flat=True).distinct().order_by("end_date"),
        }
    return render(request, "courses/list.html", {
        "courses": courses,
        "query": query,
        "selected_credits": selected_credits,
        "selected_start_date": selected_start_date,
        "selected_end_date": selected_end_date,
        "selected_sort": selected_sort,
        **filter_options,
    })

@login_required(redirect_field_name='login')
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, "courses/detail.html", {"course": course})

@login_required(redirect_field_name='login')
def course_create(request):
    if not user_is_teacher(request.user):
        messages.error(request, "Only teachers can create courses.")
        return redirect("home")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, "Course created successfully.")
            return redirect(course.get_absolute_url())
    else:
        form = CourseForm()
    return render(request, "courses/new.html", {"form": form})

@login_required(redirect_field_name='login')
def course_edit(request, pk):
    if not user_is_teacher(request.user):
        messages.error(request, "Only teachers can edit courses.")
        return redirect("home")

    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully.")
            return redirect(course.get_absolute_url())
    else:
        form = CourseForm(instance=course)
    return render(request, "courses/edit.html", {"form": form})

@login_required(login_url='login')
def course_delete(request, pk):
    if not user_is_teacher(request.user):
        messages.error(request, "Only teachers can delete courses.")
        return redirect("home")
    
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course was successfully destroyed.")
        return redirect("home")
    return render(request, "courses/delete_confirm.html", {"course": course})

@login_required(redirect_field_name='login')
def course_enroll(request, pk):
    if request.method != "POST":
        return redirect("course_detail", pk=pk)

    if user_is_teacher(request.user):
        messages.error(request, "Teachers cannot register for courses.")
        return redirect("course_detail", pk=pk)

    course = get_object_or_404(Course, pk=pk)
    account = get_object_or_404(Account, user=request.user)
    if account.enrolled_courses.filter(pk=course.pk).exists():
        messages.warning(request, "You are already registered in this course.")
        return redirect(course.get_absolute_url())

    account.enrolled_courses.add(course)
    messages.success(request, "Enrolled in course successfully.")
    return redirect(course.get_absolute_url())

@login_required(redirect_field_name='login')
def course_drop(request, pk):
    if request.method != "POST":
        return redirect("course_detail", pk=pk)

    if user_is_teacher(request.user):
        messages.error(request, "Teachers cannot drop courses.")
        return redirect("course_detail", pk=pk)

    course = get_object_or_404(Course, pk=pk)
    account = get_object_or_404(Account, user=request.user)
    if not account.enrolled_courses.filter(pk=course.pk).exists():
        messages.warning(request, "You are not registered in this course.")
        return redirect(course.get_absolute_url())

    account.enrolled_courses.remove(course)
    messages.success(request, "Course was successfully dropped.")
    return redirect(course.get_absolute_url())

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password1'])
            new_user.save()
            Account.objects.create(user=new_user)
            login(request, new_user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
        messages.error(request, "Please fill out the registration form to create an account.")
    return render(request, 'account/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm(request)
    return render(request, "account/login.html", {"form": form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Logged out successfully.")
    return redirect("login")

