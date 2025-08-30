import os
import sys
import django
import requests
# import json
from datetime import datetime, timedelta
from gql import Client, gql
# from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'alx-backend-graphql_crm.settings')
django.setup()


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


def send_order_reminders():
    # GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

    seven_days_ago = (datetime.now() - timedelta(days=7)
                      ).strftime('%Y-%m-dT%H:%M:%S')

    # Create a GraphQL client using the defined transport
    # client = Client(transport=transport, headers={
    #               'Content-Type': 'application/json'})

    query = '''
        query RecentOrders($since:DateTime!) {
            allOrder(filter: {orderDateGte: $since }) {
                edges {
                    node {
                        id
                        customer{
                            email
                            name
                        }
                        orderDate
                        totalAmount
                    }
                }
            }
        }
    '''

    variable_values = {
        "since": seven_days_ago
    }

    try:
        # response = requests.post(
        #    GRAPHQL_ENDPOINT,
        #    json={'query': query, 'variables': variables},
        # )

        result = execute_query(query, variables=variable_values)
        print(result)
        return result
        # if response.status_code == 200:
        #     data = response.json()
        #     orders = data.get('data', {}).get(
        #         'allOrders', {}).get('edges', [])

        #     log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        #     f"- Processing {len(orders)} recent orders\n"

        #     for order_edge in orders:
        #         order = order_edge['node']
        #         log_message += f"Order ID: {order['id']},"
        #         f"Customer:{order['customer']['name']},"
        #         f"Email: {order['customer']['email']},"
        #         f"Amount: ${float(order['totalAmount']):.2f}\n"

        #     with open('/tmp/order_reminders_log.txt', 'a') as f:
        #         f.write(log_message + "\n")

        #     print("Order reminders processed!")
        #     return True

        # else:
        #     error_msg = f"GraphQL query failed: {response.status_code}"
        #     with open('/tmp/order_reminders_log.txt', 'a') as f:
        #         f.write(
        #             f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        #             f"- {error_msg}\n")
        #     return False

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                f"- {error_msg}\n")
        return False


if __name__ == "__main__":
    send_order_reminders()
