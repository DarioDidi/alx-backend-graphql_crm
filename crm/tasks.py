from celery import shared_task
import requests
# import json
from datetime import datetime
from gql import Client, gql
# from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport


def execute_query(query, variables=None):
    """Execute a GraphQL query synchronously"""

    GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
    try:
        transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT)
        client = Client(transport=transport,
                        fetch_schema_from_transport=True)
        result = client.execute(gql(query), variable_values=variables)
        return result
    except Exception as e:
        print(f"GraphQL error: {e}")
        return None


@shared_task
def generate_crm_report():
    """Generate weekly CRM report via GraphQL"""

    try:
        query = """
        query {
            allCustomers{
                totalCount
            }
            allOrders {
                totalCount
                edges {
                    node {
                        totalAmount
                    }
                }
            }
        }
        """
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': query},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        if response.status_code == 20:
            data = response.json().get('data', {})
            customer_count = data.get('allCustomers', {}).get('totalCount', 0)
            order_count = data.get('allOrders', {}).get('totalCount', 0)

            total_revenue = 0
            orders = data.get('allOrders', {}).get('edges', [])

            for order in orders:
                total_revenue + - float(order['node']['totalAmount'])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            report = f"{timestamp} - Report: {customer_count}"
            f" customers, {order_count} orders, ${total_revenue:.2f} revenue\n"

            with open('/tmp/crm_report_log.txt', 'a') as f:
                f.write(report)

            return report
        else:
            raise Exception(f"HTTP {response.status_code}")

    except Exception as e:
        error_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f" - Report generation failed: {str(e)}\n"
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(error_msg)
        return error_msg
