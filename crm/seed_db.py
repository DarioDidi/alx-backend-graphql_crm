import requests
import json
from faker import Faker
import random
from datetime import datetime, timedelta

# Configuration
GRAPHQL_ENDPOINT = "http://0.0.0.0:8000/graphql/"
fake = Faker()


def execute_graphql(query, variables=None):
    """Helper function to execute GraphQL queries"""
    headers = {'Content-Type': 'application/json'}
    payload = {'query': query}
    if variables:
        payload['variables'] = variables

    response = requests.post(
        GRAPHQL_ENDPOINT,
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Query failed: {response.status_code} - {response.text}")


# def clear_existing_data():
#    """Clear all existing data (optional)"""
#    print("Clearing existing data...")
#    # Note: You would need to implement delete mutations in your schema for this
#    # This is just a placeholder showing how you might do it
#    query = """
#    mutation {
#        deleteAllOrders { success }
#        deleteAllProducts { success }
#        deleteAllCustomers { success }
#    }
#    """
#    try:
#        execute_graphql(query)
#    except Exception as e:
#        print(f"Couldn't clear data (might not be implemented): {e}")


def create_customers(count=5):
    """Create customers via GraphQL"""
    print(f"Creating {count} customers...")
    customers = []

    for _ in range(count):
        print("in create customers for loop")
        query = """
        mutation CreateCustomer($input: CustomerInput!) {
            createCustomer(input: $input) {
                customer {
                    databaseId
                    name
                    email
                }
            }
        }
        """

        variables = {
            "input": {
                "name": fake.name(),
                "email": fake.unique.email(),
                # "phone": fake.phone_number()[:20]
                "phone": '+123456789'
            }
        }

        result = execute_graphql(query, variables)
        if result:
            print("gql result ready:", result)
            customers.append(result['data']['createCustomer']['customer'])
        else:
            print("gql ERROR result:", result)

    return customers


def create_products(count=10):
    """Create products via GraphQL"""
    print(f"Creating {count} products...")
    products = []
    categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Toys']

    for _ in range(count):
        query = """
        mutation CreateProduct($input: ProductInput!) {
            createProduct(input: $input) {
                product {
                    databaseId
                    name
                    price
                }
            }
        }
        """
        variables = {
            "input": {
                "name": f"{random.choice(categories)} {fake.word().capitalize()}",
                # Convert to string for Decimal
                "price": str(round(random.uniform(5, 1000), 2)),
                "stock": random.randint(0, 100)
            }
        }
        result = execute_graphql(query, variables)
        products.append(result['data']['createProduct']['product'])

    return products


def create_orders(customers, products, count=15):
    """Create orders via GraphQL"""
    print(f"Creating {count} orders...")
    print(f"creating orders with customers:{customers}")

    for _ in range(count):
        customer = random.choice(customers)
        product_sample = random.sample(
            products, k=random.randint(1, min(5, len(products))))

        query = """
        mutation CreateOrder($input: OrderInput!) {
            createOrder(input: $input) {
                order {
                    id
                    customer { name }
                    products { name }
                    totalAmount
                }
            }
        }
        """
        variables = {
            "input": {
                "customerId": customer['databaseId'],
                "productIds": [p['databaseId'] for p in product_sample],
                "orderDate": (datetime.now() -
                              timedelta(days=random.randint(0, 90)))
                .isoformat()
            }
        }
        result = execute_graphql(query, variables)
        print("order result:", result)
        print(f"Created order: {result['data']['createOrder']['order']['id']}")


def seed_database():
    """Main seeding function"""
    print("Starting database seeding via GraphQL API...")

    # Clear existing data if needed
    # clear_existing_data()

    # Create test data
    customers = create_customers()
    products = create_products()
    create_orders(customers, products)

    print("\nDatabase seeding completed successfully!")
    print(f"Created: {len(customers)} customers")
    print(f"Created: {len(products)} products")


if __name__ == '__main__':
    seed_database()
