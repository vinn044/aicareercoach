"""Database ownership lives here; parsing and ranking remain in teammates' modules."""
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse

class User(AbstractUser):
    email = models.EmailField(unique=True)
    class Meta:
        constraints = [models.UniqueConstraint(Lower('email'), name='unique_user_email_ci')]

class Resume(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=120)
    # Paste text for this first slice. Private PDF ingestion belongs to parser integration.
    text = models.TextField(max_length=50000)
    major = models.CharField(max_length=160, blank=True)
    minor = models.CharField(max_length=160, blank=True)
    structured_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-updated_at', '-pk']
    def __str__(self): return self.title
    def get_absolute_url(self): return reverse('resume_detail', args=[self.pk])

class Feedback(models.Model):
    class Kind(models.TextChoices):
        GRAMMAR = 'grammar', 'Grammar'
        WORDING = 'wording', 'Wording'
        CONSISTENCY = 'consistency', 'Consistency'
    class Status(models.TextChoices):
        OPEN = 'open', 'Needs review'
        RESOLVED = 'resolved', 'Corrected'
        DISMISSED = 'dismissed', 'Dismissed'
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='feedback')
    kind = models.CharField(max_length=20, choices=Kind.choices)
    message = models.TextField(max_length=2000)
    evidence = models.TextField(max_length=2000, blank=True)
    suggestion = models.TextField(max_length=2000, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

class JobMatch(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='matches')
    external_id = models.CharField(max_length=160)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    url = models.URLField(max_length=1000, blank=True)
    score = models.FloatField()
    explanation = models.TextField(max_length=4000, blank=True)
    class Meta:
        ordering = ['-score', 'pk']
        constraints = [models.UniqueConstraint(fields=['resume', 'external_id'], name='unique_resume_job'),
                       models.CheckConstraint(condition=models.Q(score__gte=-1, score__lte=1), name='cosine_score_range')]

class AuthQuota(models.Model):
    # Store only keyed IP digests; never store passwords or submitted resume data here.
    key = models.CharField(max_length=64)
    bucket = models.BigIntegerField()
    count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    class Meta:
        constraints = [models.UniqueConstraint(fields=['key', 'bucket'], name='unique_auth_bucket')]
