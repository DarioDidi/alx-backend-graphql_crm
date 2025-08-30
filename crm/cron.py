from crm.models import Customer, Product, Order
import os
import django
from datetime import datetime
import requests
# import json
# from gql.transport.requests import RequestsHTTPTransport
# from gql import gql, Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'alx-backend-graphql_crm.settings')
django.setup()


GRAPHQL_ENDPOINT = "http://localhost:8000/graphql/"


def log_crm_heartbeat():
    """Log CRM heartbeat every 5 minutes"""

    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')

    customer_count = Customer.objects.count()
    product_count = Product.objects.count()
    order_count = Order.objects.count()
    message = f"{timestamp} CRM is alive - Customers: {customer_count},"
    f"Products: {product_count}, Orders: {order_count}"
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

    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
        f.write(message + "\n")

    return message


def update_low_stock():
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={'query': '''
                mutation {
                updateLowStockProducts {
                    success
                    message
                    product{
                        id
                        name
                        stock
                        price
                    }

                }
            }
            '''},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {}).get('updateLowStockProducts', {})

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"{timestamp} - "
            f"{data.get('message', 'Unknown result')}\n"

            if data.get('success') and data.get('products'):
                for product in data['products']:
                    log_message += f"  {product['name']}: {product['stock']}"
                    f" units (${float(product['price']):.2f})\n"

            with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                f.write(log_message + "\n")

            return True
        else:
            raise Exception(f"HTTP {response.status_code}")

    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_msg = f"{timestamp} - Error updating low stock: {str(e)}\n"
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(error_msg)
        return False
