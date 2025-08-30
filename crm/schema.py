import re
from decimal import Decimal
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
# from graphene_django.rest_framework.mutation import SerializerMutation
from graphql import GraphQLError

from django.db import transaction


from crm.models import Customer, Product, Order
from .filters import CustomerFilter, OrderFilter, ProductFilter


class CustomerType(DjangoObjectType):
    database_id = graphene.Int()

    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node, )
        filterset_class = CustomerFilter

    def resolve_database_id(self, info):
        return self.id


class ProductType(DjangoObjectType):
    database_id = graphene.Int()

    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter

    def resolve_database_id(self, info):
        return self.id


class OrderType(DjangoObjectType):
    products = graphene.List(ProductType)

    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter

    def resolve_products(self, info):
        return self.products.all()


class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


class CreateCustomer(graphene.Mutation):
    # class CreateCustomer(SerializerMutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def validate_phone_format(phone):
        if phone and not re.match(r"^(\+\d{1,3}[-]?)?\d{7,10}$", phone):
            raise GraphQLError(
                "Invalid phone format. Use +1234567890 or 123-456-7890 NOT:"
            )

    def mutate(self, info, input):
        try:
            CreateCustomer.validate_phone_format(input.phone)
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            return CreateCustomer(
                customer=customer,
                message="Customer created successfully"
            )

        except Exception as e:
            raise GraphQLError(str(e))


class BulkCreateCustomers(graphene.Mutation):
    # class BulkCreateCustomers(SerializerMutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        customers = []
        errors = []

        for i, customer_input in enumerate(input):
            try:
                CreateCustomer.validate_phone_format(customer_input.phone)
                customer = Customer(
                    name=customer_input.name,
                    email=customer_input.email,
                    phone=customer_input.phone
                )
                customer.full_clean()
                customer.save()

                customers.append(customer)

            # partial success by storing errors and continue
            except Exception as e:
                errors.append(f"Row {i + 1}: {str(e)}")

        return BulkCreateCustomers(customers=customers, errors=errors)


class CreateProduct(graphene.Mutation):
    # class CreateProduct(SerializerMutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise GraphQLError("Price must be > 0")
        if input.stock and input.stock < 0:
            raise GraphQLError("Stock cannot be negative")

        product = Product(
            name=input.name,
            price=Decimal(input.price),
            stock=input.stock if input.stock is not None else 0
        )
        product.full_clean()
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    # class CreateOrder(SerializerMutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @transaction.atomic
    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Customer does not exist")

        if not input.product_ids:
            raise GraphQLError("At least one product is required")

        products = []
        total_amount = 0

        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=input.order_date if input.order_date else None
        )

        for product_id in input.product_ids:
            try:
                product = Product.objects.get(pk=product_id)
                products.append(product)
                order.products.add(product)
                total_amount += Decimal(product.price)
            except Product.DoesNotExist:
                raise GraphQLError(
                    f"Product with ID {product_id} does not exist")

        # order.products.set(products)
        order.full_clean()
        order.save()
        return CreateOrder(order=order)


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    customer = graphene.Field(CustomerType, id=graphene.ID())
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)

    def resolve_customer(self, info, id):
        return Customer.objects.get(pk=id)


class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    products = graphene.List(ProductType)
    message = graphene.String()
    success = graphene.Boolean()

    def mutate(self, info):
        from django.db import transaction

        try:
            with transaction.atomic():
                low_stock_products = Product.objects.filter(stock__lt=10)
                updated_products = []

                # Increments their stock by 10 (simulating restocking).
                for product in low_stock_products:
                    product.stock += 10
                    product.save()
                    updated_products.append(product)

                return UpdateLowStockProducts(
                    product=updated_products,
                    message=f"Updated {len(updated_products)}"
                    f" low-stock products",
                    success=True
                )

        except Exception as e:
            return UpdateLowStockProducts(
                products=[],
                message=f"Error updating low-stock products: {str(e)}",
                success=False
            )


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
