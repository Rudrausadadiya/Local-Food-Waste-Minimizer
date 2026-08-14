from typing import Optional, List, Dict, Any
from django.db.models import QuerySet, Prefetch
from .models import Customer, Order, OrderItem, Payment, Invoice, Sale, LoyaltyTransaction, Delivery

# Class: CustomerRepository
class CustomerRepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(customer_id: str) -> Optional[Customer]:
        return Customer.objects.filter(id=customer_id, is_deleted=False).first()
        
    @staticmethod
    # Method: get_by_business
    def get_by_business(business_id: str) -> QuerySet:
        return Customer.objects.filter(business_id=business_id, is_deleted=False)
        
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> Customer:
        return Customer.objects.create(**data)
        
    @staticmethod
    # Method: update
    def update(customer: Customer, data: Dict[str, Any]) -> Customer:
        for key, value in data.items():
            setattr(customer, key, value)
        customer.save()
        return customer

    @staticmethod
    # Method: soft_delete
    def soft_delete(customer: Customer) -> None:
        customer.is_deleted = True
        customer.is_active = False
        customer.save(update_fields=['is_deleted', 'is_active', 'updated_at'])

# Class: OrderRepository
class OrderRepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(order_id: str) -> Optional[Order]:
        return Order.objects.filter(id=order_id, is_deleted=False).first()

    @staticmethod
    # Method: get_by_id_with_items
    def get_by_id_with_items(order_id: str) -> Optional[Order]:
        return Order.objects.prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('product'))
        ).filter(id=order_id, is_deleted=False).first()
        
    @staticmethod
    # Method: get_by_id_for_update
    def get_by_id_for_update(order_id: str) -> Optional[Order]:
        return Order.objects.select_for_update().filter(id=order_id, is_deleted=False).first()
        
    @staticmethod
    # Method: get_by_business
    def get_by_business(business_id: str) -> QuerySet:
        return Order.objects.filter(business_id=business_id, is_deleted=False)
        
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> Order:
        return Order.objects.create(**data)
        
    @staticmethod
    # Method: update
    def update(order: Order, data: Dict[str, Any]) -> Order:
        for key, value in data.items():
            setattr(order, key, value)
        order.save()
        return order
        
    @staticmethod
    # Method: add_items
    def add_items(order: Order, items_data: List[Dict[str, Any]]) -> List[OrderItem]:
        items = [OrderItem(order=order, **item_data) for item_data in items_data]
        return OrderItem.objects.bulk_create(items)

    @staticmethod
    # Method: soft_delete
    def soft_delete(order: Order) -> None:
        order.is_deleted = True
        order.save(update_fields=['is_deleted', 'updated_at'])

# Class: PaymentRepository
class PaymentRepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(payment_id: str) -> Optional[Payment]:
        return Payment.objects.filter(id=payment_id).first()
        
    @staticmethod
    # Method: get_by_order
    def get_by_order(order_id: str) -> QuerySet:
        return Payment.objects.filter(order_id=order_id)
        
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> Payment:
        return Payment.objects.create(**data)
        
    @staticmethod
    # Method: update
    def update(payment: Payment, data: Dict[str, Any]) -> Payment:
        for key, value in data.items():
            setattr(payment, key, value)
        payment.save()
        return payment

# Class: InvoiceRepository
class InvoiceRepository:
    @staticmethod
    # Method: get_by_order
    def get_by_order(order_id: str) -> Optional[Invoice]:
        return Invoice.objects.filter(order_id=order_id).first()
        
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> Invoice:
        return Invoice.objects.create(**data)

# Class: SaleRepository
class SaleRepository:
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> Sale:
        return Sale.objects.create(**data)

# Class: LoyaltyTransactionRepository
class LoyaltyTransactionRepository:
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> LoyaltyTransaction:
        return LoyaltyTransaction.objects.create(**data)

    @staticmethod
    # Method: get_by_customer
    def get_by_customer(customer_id: str) -> QuerySet:
        return LoyaltyTransaction.objects.filter(customer_id=customer_id)

# Class: DeliveryRepository
class DeliveryRepository:
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> Delivery:
        return Delivery.objects.create(**data)

    @staticmethod
    # Method: get_by_id
    def get_by_id(delivery_id: str) -> Optional[Delivery]:
        return Delivery.objects.filter(id=delivery_id).first()

    @staticmethod
    # Method: update
    def update(delivery: Delivery, data: Dict[str, Any]) -> Delivery:
        for key, value in data.items():
            setattr(delivery, key, value)
        delivery.save()
        return delivery


