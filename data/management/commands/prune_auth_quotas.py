from django.core.management.base import BaseCommand
from django.utils import timezone
from data.models import AuthQuota
class Command(BaseCommand):
    help = 'Delete expired authentication rate-limit counters.'
    def handle(self, *args, **options):
        count, _ = AuthQuota.objects.filter(expires_at__lt=timezone.now()).delete()
        self.stdout.write(f'Deleted {count} expired counters.')
