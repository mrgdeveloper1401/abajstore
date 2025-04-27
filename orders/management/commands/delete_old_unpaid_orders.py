from django.core.management.base import BaseCommand
from django.utils import timezone
from jdatetime import datetime, timedelta
from orders.models import Order


class Command(BaseCommand):
    help = 'Delete orders that are older than one hour and have not been paid'

    def handle(self, *args, **kwargs):
        one_day_ago = timezone.now() - timedelta(days=1)

        orders_to_delete = Order.objects.filter(
            created__lte=one_day_ago,
            status='در انتظار پرداخت'
        )

        count, _ = orders_to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} orders.'))
