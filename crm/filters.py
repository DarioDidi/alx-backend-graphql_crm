import django_filters

from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    phone_pattern = django_filters.CharFilter(method='filter_phone_pattern')

    class Meta:
        model = Customer
        fields = {
            'name': ['icontains'],
            'email': ['icontains'],
            'created_at': ['gte', 'lte']
        }

        def filter_phone_pattern(self, queryset, name, value):
            return queryset.filter(phone__startswith=value)


class ProductFilter(django_filters.FilterSet):
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')

    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'price': ['gte', 'lte'],
            'stock': ['gte', 'lte']
        }

        def filter_low_stock(self, queryset, name, value):
            if value:
                return queryset.filter(stock__lt=10)
            return queryset


class OrderFilter(django_filters.FilterSet):
    customer_name = django_filters.CharFilter(
        field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(
        field_name='products__name', lookup_expr='icontains')
    product_id = django_filters.CharFilter(field_name='products__id')

    class Meta:
        model = Order
        fields = fields = {
            'total_amount': ['gte', 'lte'],
            'order_date': ['gte', 'lte'],
        }
