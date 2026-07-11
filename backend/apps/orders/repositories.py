from typing import Optional, List, Dict, Any
from django.db.models import QuerySet, Prefetch, Sum
from .models import Customer, Order, OrderItem, Payment, Invoice, Sale, LoyaltyTransaction, Delivery

class CustomerRepository:
    @staticmethod
    def get_by_id(customer_id: str) -> Optional[Customer]:
        return Customer.objects.filter(id=customer_id, is_deleted=False).first()
        
    @staticmethod
    def get_by_business(business_id: str) -> QuerySet:
        return Customer.objects.filter(business_id=business_id, is_deleted=False)
        
    @staticmethod
    def create(data: Dict[str, Any]) -> Customer:
        return Customer.objects.create(**data)
        
    @staticmethod
    def update(customer: Customer, data: Dict[str, Any]) -> Customer:
        for key, value in data.items():
            setattr(customer, key, value)
        customer.save()
        return customer

    @staticmethod
    def soft_delete(customer: Customer) -> None:
        customer.is_deleted = True
        customer.is_active = False
        customer.save(update_fields=['is_deleted', 'is_active', 'updated_at'])

class OrderRepository:
    @staticmethod
    def get_by_id(order_id: str) -> Optional[Order]:
        return Order.objects.filter(id=order_id, is_deleted=False).first()

    @staticmethod
    def get_by_id_with_items(order_id: str) -> Optional[Order]:
        return Order.objects.prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('product'))
        ).filter(id=order_id, is_deleted=False).first()
        
    @staticmethod
    def get_by_id_for_update(order_id: str) -> Optional[Order]:
        return Order.objects.select_for_update().filter(id=order_id, is_deleted=False).first()
        
    @staticmethod
    def get_by_business(business_id: str) -> QuerySet:
        return Order.objects.filter(business_id=business_id, is_deleted=False)
        
    @staticmethod
    def create(data: Dict[str, Any]) -> Order:
        return Order.objects.create(**data)
        
    @staticmethod
    def update(order: Order, data: Dict[str, Any]) -> Order:
        for key, value in data.items():
            setattr(order, key, value)
        order.save()
        return order
        
    @staticmethod
    def add_items(order: Order, items_data: List[Dict[str, Any]]) -> List[OrderItem]:
        items = [OrderItem(order=order, **item_data) for item_data in items_data]
        return OrderItem.objects.bulk_create(items)

    @staticmethod
    def soft_delete(order: Order) -> None:
        order.is_deleted = True
        order.save(update_fields=['is_deleted', 'updated_at'])

class PaymentRepository:
    @staticmethod
    def get_by_id(payment_id: str) -> Optional[Payment]:
        return Payment.objects.filter(id=payment_id).first()
        
    @staticmethod
    def get_by_order(order_id: str) -> QuerySet:
        return Payment.objects.filter(order_id=order_id)
        
    @staticmethod
    def create(data: Dict[str, Any]) -> Payment:
        return Payment.objects.create(**data)
        
    @staticmethod
    def update(payment: Payment, data: Dict[str, Any]) -> Payment:
        for key, value in data.items():
            setattr(payment, key, value)
        payment.save()
        return payment

class InvoiceRepository:
    @staticmethod
    def get_by_order(order_id: str) -> Optional[Invoice]:
        return Invoice.objects.filter(order_id=order_id).first()
        
    @staticmethod
    def create(data: Dict[str, Any]) -> Invoice:
        return Invoice.objects.create(**data)

class SaleRepository:
    @staticmethod
    def create(data: Dict[str, Any]) -> Sale:
        return Sale.objects.create(**data)
