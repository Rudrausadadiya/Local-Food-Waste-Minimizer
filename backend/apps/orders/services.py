from typing import Dict, Any, List
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Order, Invoice, Payment, PaymentStatus, OrderStatus, PaymentGateway, Delivery
from .repositories import (
    OrderRepository, PaymentRepository, InvoiceRepository, SaleRepository,
    CustomerRepository, LoyaltyTransactionRepository, DeliveryRepository
)
from apps.inventory.services import InventoryService
from apps.inventory.models import Inventory
from .signals import (
    order_created, order_completed, order_cancelled,
    payment_completed, payment_failed, invoice_generated,
    refund_completed, inventory_reserved, inventory_released
)
from django.core.exceptions import ValidationError


# Class: OrderService
class OrderService:
    @staticmethod
    @transaction.atomic
    # Method: create_order
    def create_order(order_data: Dict[str, Any], items_data: List[Dict[str, Any]]) -> Order:
        # Extract optional loyalty points redemption and delivery address
        redeem_points = int(order_data.pop('redeem_points', 0) or 0)
        delivery_address_param = order_data.pop('delivery_address', None)
        customer = order_data.get('customer')

        # Early validation: Validate loyalty points redemption BEFORE reserving inventory
        if redeem_points > 0:
            if not customer:
                raise ValidationError("Customer is required to redeem loyalty points.")
            if redeem_points > customer.loyalty_points:
                raise ValidationError(f"Cannot redeem {redeem_points} points; customer only has {customer.loyalty_points} points available.")

        # Calculate totals
        subtotal = Decimal('0.00')
        tax_total = Decimal('0.00')
        discount_total = Decimal(str(redeem_points)) if redeem_points > 0 else Decimal('0.00')
        
        # Prepare item data and validate/reserve inventory
        for item in items_data:
            quantity = Decimal(str(item['quantity']))
            unit_price = Decimal(str(item['unit_price']))
            tax_rate = Decimal(str(item.get('tax_rate', '0.00')))
            discount = Decimal(str(item.get('discount', '0.00')))
            
            total_price = (quantity * unit_price) + tax_rate - discount
            item['total_price'] = total_price
            
            subtotal += quantity * unit_price
            tax_total += tax_rate
            discount_total += discount
            
            # Reserve inventory
            inventory = Inventory.objects.filter(
                product_id=item['product'].id, 
                branch_id=order_data['branch'].id
            ).first()
            if inventory:
                InventoryService.reserve_stock(inventory.id, quantity)
                inventory_reserved.send(sender=OrderService, inventory=inventory, quantity=quantity)

        delivery_charge = Decimal(str(order_data.get('delivery_charge', '0.00')))
        total_amount = max(Decimal('0.00'), subtotal + tax_total + delivery_charge - discount_total)
        
        order_data['subtotal'] = subtotal
        order_data['tax_amount'] = tax_total
        order_data['discount_amount'] = discount_total
        order_data['total_amount'] = total_amount
        
        order = OrderRepository.create(order_data)
        OrderRepository.add_items(order, items_data)
        
        if redeem_points > 0 and customer:
            CustomerRepository.update(customer, {'loyalty_points': customer.loyalty_points - redeem_points})
            LoyaltyTransactionRepository.create({
                'customer': customer,
                'order': order,
                'points': -redeem_points,
                'description': f"Redeemed at checkout for order {order.order_number}"
            })

        if order.order_type == 'DELIVERY':
            address_str = delivery_address_param or (customer.address if customer else '') or 'Delivery Address Unspecified'
            DeliveryRepository.create({
                'order': order,
                'delivery_address': address_str,
                'status': 'PENDING'
            })

        order_created.send(sender=OrderService, order=order)
        return order

    @staticmethod
    @transaction.atomic
    # Method: cancel_order
    def cancel_order(order_id: str) -> Order:
        order = OrderRepository.get_by_id_for_update(order_id)
        if not order:
            raise ValidationError("Order not found.")
        if order.order_status == OrderStatus.COMPLETED:
            raise ValidationError("Cannot modify completed orders.")
            
        order = OrderRepository.update(order, {'order_status': OrderStatus.CANCELLED})
        
        # Restore reserved inventory
        for item in order.items.all():
            inventory = Inventory.objects.filter(
                product_id=item.product_id, 
                branch_id=order.branch_id
            ).first()
            if inventory:
                InventoryService.release_stock(inventory.id, Decimal(str(item.quantity)))
                inventory_released.send(sender=OrderService, inventory=inventory, quantity=Decimal(str(item.quantity)))
                
        order_cancelled.send(sender=OrderService, order=order)
        return order

    @staticmethod
    @transaction.atomic
    # Method: complete_order
    def complete_order(order_id: str) -> Order:
        order = OrderRepository.get_by_id_for_update(order_id)
        if not order:
            raise ValidationError("Order not found.")
        
        if order.payment_status != PaymentStatus.COMPLETED and order.payment_method != PaymentGateway.CASH:
            raise ValidationError("Cannot complete unpaid orders unless payment method allows COD.")
            
        order = OrderRepository.update(order, {'order_status': OrderStatus.COMPLETED})
        
        # Create Sale Record
        SaleRepository.create({
            'order': order,
            'business': order.business,
            'branch': order.branch,
            'revenue': order.total_amount,
            'tax_collected': order.tax_amount
        })

        # Award loyalty points on order completion (1 point per ₹100 spent, min 1 point)
        if order.customer:
            points_earned = max(1, int(order.total_amount // 100))
            if points_earned > 0:
                LoyaltyTransactionRepository.create({
                    'customer': order.customer,
                    'order': order,
                    'points': points_earned,
                    'description': f"Earned from order {order.order_number}"
                })
                CustomerRepository.update(order.customer, {'loyalty_points': order.customer.loyalty_points + points_earned})
        
        order_completed.send(sender=OrderService, order=order)
        return order

    @staticmethod
    @transaction.atomic
    # Method: delete_order
    def delete_order(order_id: str) -> None:
        order = OrderRepository.get_by_id_for_update(order_id)
        if not order:
            raise ValidationError("Order not found.")
        if order.payment_status == PaymentStatus.COMPLETED:
            raise ValidationError("Cannot delete paid orders.")
        if order.order_status == OrderStatus.COMPLETED:
            raise ValidationError("Cannot modify completed orders.")
        OrderRepository.soft_delete(order)


# Class: DeliveryService
class DeliveryService:
    @staticmethod
    @transaction.atomic
    # Method: dispatch_delivery
    def dispatch_delivery(delivery_id: str) -> Delivery:
        delivery = DeliveryRepository.get_by_id(delivery_id)
        if not delivery:
            raise ValidationError("Delivery record not found.")
        if delivery.status in ['DISPATCHED', 'DELIVERED']:
            raise ValidationError(f"Delivery is already {delivery.status.lower()}.")
        return DeliveryRepository.update(delivery, {
            'status': 'DISPATCHED',
            'dispatched_at': timezone.now()
        })

    @staticmethod
    @transaction.atomic
    # Method: mark_delivered
    def mark_delivered(delivery_id: str) -> Delivery:
        delivery = DeliveryRepository.get_by_id(delivery_id)
        if not delivery:
            raise ValidationError("Delivery record not found.")
        if delivery.status == 'DELIVERED':
            raise ValidationError("Delivery is already delivered.")
        if delivery.status != 'DISPATCHED':
            raise ValidationError("Delivery must be dispatched before marking delivered.")
        return DeliveryRepository.update(delivery, {
            'status': 'DELIVERED',
            'delivered_at': timezone.now()
        })


# Class: PaymentService
class PaymentService:
    @staticmethod
    @transaction.atomic
    # Method: process_payment
    def process_payment(order_id: str, payment_data: Dict[str, Any]) -> Payment:
        order = OrderRepository.get_by_id_for_update(order_id)
        if not order:
            raise ValidationError("Order not found.")
            
        if order.order_status == OrderStatus.COMPLETED:
            raise ValidationError("Cannot modify completed orders.")
            
        payment_data['order'] = order
        payment = PaymentRepository.create(payment_data)
        
        if payment.payment_status == PaymentStatus.COMPLETED:
            OrderRepository.update(order, {'payment_status': PaymentStatus.COMPLETED})
            payment_completed.send(sender=PaymentService, payment=payment)
            
            # Deduct inventory using FIFO
            for item in order.items.all():
                inventory = Inventory.objects.filter(
                    product_id=item.product_id, 
                    branch_id=order.branch_id
                ).first()
                if inventory:
                    # Release reservation and permanently deduct
                    qty = Decimal(str(item.quantity))
                    InventoryService.release_stock(inventory.id, qty)
                    InventoryService.stock_out(
                        inventory_id=inventory.id,
                        quantity=qty,
                        user_id=str(order.created_by.id) if order.created_by else 'system',
                        reference_number=order.order_number,
                        remarks=f"Order {order.order_number} Paid"
                    )
        else:
            payment_failed.send(sender=PaymentService, payment=payment)
            
        return payment

    @staticmethod
    @transaction.atomic
    # Method: process_refund
    def process_refund(payment_id: str) -> Payment:
        payment = PaymentRepository.get_by_id(payment_id)
        if not payment:
            raise ValidationError("Payment not found.")
            
        if payment.payment_status != PaymentStatus.COMPLETED:
            raise ValidationError("Cannot refund unpaid orders.")
            
        payment = PaymentRepository.update(payment, {'payment_status': PaymentStatus.REFUNDED})
        order = OrderRepository.get_by_id_for_update(payment.order.id)
        OrderRepository.update(order, {
            'payment_status': PaymentStatus.REFUNDED,
            'order_status': OrderStatus.REFUNDED
        })
        
        # Restore stock
        for item in order.items.all():
            inventory = Inventory.objects.filter(
                product_id=item.product_id, 
                branch_id=order.branch_id
            ).first()
            if inventory:
                InventoryService.stock_in(
                    inventory_id=inventory.id,
                    quantity=Decimal(str(item.quantity)),
                    user_id=str(order.created_by.id) if order.created_by else 'system',
                    batch_details={'batch_number': f"REF-{order.order_number}"},
                    reference_number=order.order_number,
                    remarks=f"Order {order.order_number} Refunded"
                )
                
        refund_completed.send(sender=PaymentService, payment=payment)
        return payment


# Class: InvoiceService
class InvoiceService:
    @staticmethod
    @transaction.atomic
    # Method: generate_invoice
    def generate_invoice(order_id: str) -> 'Invoice':
        order = OrderRepository.get_by_id(order_id)
        if not order:
            raise ValidationError("Order not found.")
            
        # Future hook for PDF generation without coupling to a specific library
        # e.g., pdf_file = pdf_generator_engine.generate(order)
        pdf_file = None
        
        invoice_number = f"INV-{order.order_number}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        invoice = InvoiceRepository.create({
            'order': order,
            'invoice_number': invoice_number,
            'invoice_pdf': pdf_file
        })
        
        invoice_generated.send(sender=InvoiceService, invoice=invoice)
        return invoice
