from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer
# import logging


class Command(BaseCommand):
    help = 'deletes customers with no orders since a year ago'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate the cleanup without actually deleting anything'
        )

        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days to conside inactive(default:365)'
        )

    def handle(self, *args, **kwargs):
        dry_run = kwargs['dry_run']
        days_inactive = kwargs['days']

        cutoff_date = timezone.now() - timedelta(days=days_inactive)

        self.stdout.write(self.style.NOTICE(
            "Finding customers inactive since"
            f"{cutoff_date.strftime('%Y-%m-%d')}"
        ))

        # Find inactive customers:
        # those with no orders OR only orders older than cutoff
        inactive_customers = Customer.objects.filter(
            order__isnull=True
        ) | Customer.objects.exclude(
            order__order_date__gte=cutoff_date
        ).distinct()

        deleted_count = inactive_customers.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN: Would delete {deleted_count} inactive customers"
                )
            )

            # Show some sample customers that would be deleted
            for customer in inactive_customers[:5]:  # First 5 only
                self.stdout.write(f"  - {customer.name} ({customer.email})")

            if deleted_count > 5:
                self.stdout.write(f"  - ... and {deleted_count - 5} more")

        else:
            # ACTUAL DELETE
            deleted_count, _ = inactive_customers.delete()

            log_details = f"{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            f" - Deleted {deleted_count} customers:\n"
            for customer in inactive_customers:
                log_details += f"  - {customer.name} ({customer.email})\n"

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {deleted_count} inactive customers"
                )
            )

            with open('/tmp/customer_cleanup_detailed_log.txt', 'a') as f:
                f.write(log_details)

        return deleted_count
