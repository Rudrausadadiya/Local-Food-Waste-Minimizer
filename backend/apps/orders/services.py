from typing import Dict, Any, List
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, Payment, PaymentStatus, OrderStatus, PaymentGateway
from .repositories import CustomerRepository, OrderRepository, PaymentRepository, InvoiceRepository, SaleRepository
from apps.inventory.services import InventoryService
from apps.inventory.models import Inventory
from .signals import (
    order_created, order_completed, order_cancelled,
    payment_completed, payment_failed, invoice_generated,
    refund_completed, inventory_reserved, inventory_released
)
from django.core.exceptions import ValidationError


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(order_data: Dict[str, Any], items_data: List[Dict[str, Any]]) -> Order:
        # Calculate totals
        subtotal = Decimal('0.00')
        tax_total = Decimal('0.00')
        discount_total = Decimal('0.00')
        
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
        total_amount = subtotal + tax_total + delivery_charge - discount_total
        
        order_data['subtotal'] = subtotal
        order_data['tax_amount'] = tax_total
        order_data['discount_amount'] = discount_total
        order_data['total_amount'] = total_amount
        
        order = OrderRepository.create(order_data)
        OrderRepository.add_items(order, items_data)
        
        order_created.send(sender=OrderService, order=order)
        return order

    @staticmethod
    @transaction.atomic
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
        
        order_completed.send(sender=OrderService, order=order)
        return order

    @staticmethod
    @transaction.atomic
    def delete_order(order_id: str) -> None:
        order = OrderRepository.get_by_id_for_update(order_id)
        if not order:
            raise ValidationError("Order not found.")
        if order.payment_status == PaymentStatus.COMPLETED:
            raise ValidationError("Cannot delete paid orders.")
        if order.order_status == OrderStatus.COMPLETED:
            raise ValidationError("Cannot modify completed orders.")
            
        OrderRepository.soft_delete(order)


class PaymentService:
    @staticmethod
    @transaction.atomic
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


class InvoiceService:
    @staticmethod
    @transaction.atomic
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
