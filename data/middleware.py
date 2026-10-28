"""Small database-backed request throttle, not a network firewall or DDoS defense."""
import hashlib
import hmac
import time
from datetime import datetime, timezone
from django.conf import settings
from django.db.models import F
from django.http import HttpResponse
from .models import AuthQuota

class AuthRateLimitMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        policies = {'/accounts/login/': (10, 60), '/accounts/register/': (5, 3600), '/admin/login/': (10, 60)}
        if request.method == 'POST' and request.path in policies:
            limit, seconds = policies[request.path]
            now = int(time.time())
            bucket = now // seconds
            # Forwarded IP headers can be forged. Use the direct peer until a trusted proxy is configured.
            identity = request.path + ':' + request.META.get('REMOTE_ADDR', 'unknown')
            key = hmac.new(settings.SECRET_KEY.encode(), identity.encode(), hashlib.sha256).hexdigest()
            quota, _ = AuthQuota.objects.get_or_create(key=key, bucket=bucket, defaults={
                'expires_at': datetime.fromtimestamp((bucket + 1) * seconds, timezone.utc)})
            # Atomic conditional update prevents parallel requests from bypassing the count.
            allowed = AuthQuota.objects.filter(pk=quota.pk, count__lt=limit).update(count=F('count') + 1)
            if not allowed:
                response = HttpResponse('Too many attempts. Please try again later.', status=429)
                response['Retry-After'] = str((bucket + 1) * seconds - now)
                return response
        return self.get_response(request)
