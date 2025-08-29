from crm.models import Customer, Product, Order
import os
import django
from datetime import datetime
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'alx_backend_graphql_crm.settings')
django.setup()


def log_crm_heartbeat():
    """Log CRM heartbeat every 5 minutes"""

    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')

    customer_count = Customer.objects.count()
    product_count = Product.objects.count()
    order_count = Order.objects.count()
    message = f"{timestamp} CRM is alive - Customers: {customer_count},"
    f"Products: {product_count}, Orders: {order_count}"
    GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={'query': '{hello}'},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )

        if response.status_code == 200:
            message += " - GraphQL endpoint responsive"
        else:
            message += " - GraphQL endpoint not responsive"
    except Exception as e:
        message += f" - GraphQL check failed: {str(e)}"

    return message
