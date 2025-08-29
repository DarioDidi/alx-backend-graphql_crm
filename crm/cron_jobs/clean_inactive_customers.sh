#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$PROJECT_DIR")"

cd "$PROJECT_DIR" || exit

#python manage.py shell << EOF
#from django.utils import timezone
#from datetime import timedelta
#from crm.models import Customer, Order
#import logging
#
#logger = logging.getLogger(__name__)
#
## Calculate date one year ago
#one_year_ago = timezone.now() - timedelta(days=365)
#
## Find customers with no orders OR last order older than 1 year
#inactive_customers = Customer.objects.filter(
#    order__isnull=True  # Customers with no orders
#) | Customer.objects.exclude(
#    order__order_date__gte=one_year_ago  # Customers with no recent orders
#).distinct()
#
#count = inactive_customers.count()
#inactive_customers.delete()
#
## Log results
#log_message = f"$(date '+%Y-%m-%d %H:%M:%S') - Deleted {count} inactive customers\n"
#with open('/tmp/customer_cleanup_log.txt', 'a') as f:
#    f.write(log_message)
#
#print(f"Deleted {count} inactive customers")
#EOF

python manage.py delete_inactive

#save exit status
retVal=$?

#Add error handling
if [ $retVal -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleanup completed successfully" >> /tmp/customer_cleanup_log.txt
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleanup failed" >> /tmp/customer_cleanup_log.txt
    exit 1
fi




