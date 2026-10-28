"""HTML endpoints: every student record lookup is scoped to the signed-in owner."""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from .forms import RegistrationForm, ResumeForm
from .models import Feedback, Resume

@require_http_methods(['GET', 'POST'])
def register(request):
    if request.user.is_authenticated: return redirect('home')
    form = RegistrationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic(): user = form.save()
        except IntegrityError:
            form.add_error(None, 'Unable to create this account. Check your username and email.')
        else:
            login(request, user)
            return redirect('home')
    return render(request, 'accounts/register.html', {'form': form})

@require_GET
def home(request):
    return render(request, 'home.html', {'resume_count': request.user.resumes.count() if request.user.is_authenticated else 0})

@login_required
@require_GET
def profile(request): return render(request, 'accounts/profile.html')

@login_required
@require_GET
def resume_list(request):
    query = request.GET.get('q', '')[:200]
    resumes = Resume.objects.filter(owner=request.user)
    if query: resumes = resumes.filter(Q(title__icontains=query) | Q(major__icontains=query) | Q(minor__icontains=query))
    page = Paginator(resumes, 20).get_page(request.GET.get('page'))
    return render(request, 'resumes/list.html', {'page_obj': page, 'query': query})

@login_required
@require_GET
def resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk, owner=request.user)
    return render(request, 'resumes/detail.html', {'resume': resume})

@login_required
@require_http_methods(['GET', 'POST'])
def resume_create(request):
    form = ResumeForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        resume = form.save(commit=False)
        resume.owner = request.user
        resume.save()
        messages.success(request, 'Resume saved.')
        return redirect(resume)
    return render(request, 'resumes/new.html', {'form': form})

@login_required
@require_http_methods(['GET', 'POST'])
def resume_edit(request, pk):
    resume = get_object_or_404(Resume, pk=pk, owner=request.user)
    form = ResumeForm(request.POST if request.method == 'POST' else None, instance=resume)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            # Serialize edits with analysis writes. Any change invalidates old AI output.
            locked = Resume.objects.select_for_update().get(pk=pk, owner=request.user)
            locked_form = ResumeForm(request.POST, instance=locked)
            if locked_form.is_valid():
                if locked_form.has_changed():
                    locked_form.save()
                    locked.structured_data = {}
                    locked.save(update_fields=['structured_data'])
                    locked.feedback.all().delete()
                    locked.matches.all().delete()
                messages.success(request, 'Resume updated. Reanalysis is needed for new feedback and matches.')
                return redirect(locked)
            form = locked_form
    return render(request, 'resumes/edit.html', {'form': form, 'resume': resume})

@login_required
@require_http_methods(['GET', 'POST'])
def resume_delete(request, pk):
    resume = get_object_or_404(Resume, pk=pk, owner=request.user)
    if request.method == 'POST':
        resume.delete()
        messages.success(request, 'Resume and its saved results deleted.')
        return redirect('resume_list')
    return render(request, 'resumes/delete_confirm.html', {'resume': resume})

@login_required
@require_POST
def feedback_status(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk, resume__owner=request.user)
    status = request.POST.get('status')
    if status not in Feedback.Status.values:
        from django.http import HttpResponseBadRequest
        return HttpResponseBadRequest('Invalid status.')
    feedback.status = status
    feedback.save(update_fields=['status'])
    return redirect(feedback.resume)

@login_required
@require_GET
def job_matches(request):
    # Shows persisted matching results. No model downloads or paid API calls at request time.
    from .models import JobMatch
    matches = JobMatch.objects.filter(resume__owner=request.user).select_related('resume')
    return render(request, 'matches/list.html', {'matches': matches})
