from typing import Dict, Any, List
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Reservation, ReservationStatus
from .repositories import (
    ReservationRepository, ReservationItemRepository, 
    ReservationTableRepository, ReservationHistoryRepository
)
from .validators import validate_product_active, validate_reservation_modifiable
from .signals import (
    reservation_created, reservation_confirmed, reservation_cancelled,
    reservation_expired, reservation_converted_to_order
)
from apps.inventory.services import InventoryService
from apps.inventory.models import Inventory
from apps.orders.services import OrderService


# Class: ReservationService
class ReservationService:
    @staticmethod
    @transaction.atomic
    # Method: create_reservation
    def create_reservation(reservation_data: Dict[str, Any], items_data: List[Dict[str, Any]] = None, tables_data: List[Dict[str, Any]] = None, user=None) -> Reservation:
        items_data = items_data or []
        tables_data = tables_data or []

        # Validate 15 km radius between user location and branch
        user_lat = reservation_data.pop('user_lat', None) or reservation_data.pop('latitude', None)
        user_lon = reservation_data.pop('user_lon', None) or reservation_data.pop('longitude', None)
        branch = reservation_data.get('branch')
        if branch:
            from common.utils import get_branch_coordinates, validate_15km_radius
            target_lat, target_lon = get_branch_coordinates(branch)
            validate_15km_radius(user_lat, user_lon, target_lat, target_lon, entity_name="table or food reservation")

        # Table Overlap Validation
        table_ids = [str(t['table'].id) for t in tables_data if 'table' in t]
        if table_ids:
            has_overlap = ReservationTableRepository.check_overlap(
                table_ids=table_ids,
                res_date=reservation_data['reservation_date'],
                res_start_time=reservation_data['reservation_time'],
                res_end_time=reservation_data['expected_duration']
            )
            if has_overlap:
                raise ValidationError("One or more tables are already reserved for this time slot.")

        # Validate products
        for item in items_data:
            validate_product_active(item['product'])

        reservation_data['reservation_status'] = ReservationStatus.PENDING
        reservation = ReservationRepository.create(reservation_data)

        if items_data:
            ReservationItemRepository.add_items(reservation, items_data)
        if tables_data:
            ReservationTableRepository.add_tables(reservation, tables_data)

        ReservationHistoryRepository.log_history(
            reservation=reservation,
            previous_status=None,
            new_status=ReservationStatus.PENDING,
            changed_by=user,
            remarks="Reservation created."
        )

        reservation_created.send(sender=ReservationService, reservation=reservation)
        return reservation

    @staticmethod
    @transaction.atomic
    # Method: confirm_reservation
    def confirm_reservation(reservation_id: str, user=None) -> Reservation:
        reservation = ReservationRepository.get_by_id_for_update(reservation_id)
        if not reservation:
            raise ValidationError("Reservation not found.")
            
        validate_reservation_modifiable(reservation)

        # Reserve inventory for products
        for item in reservation.items.all():
            inventory = Inventory.objects.filter(
                product_id=item.product_id, 
                branch_id=reservation.branch_id
            ).first()
            if inventory:
                InventoryService.reserve_stock(str(inventory.id), Decimal(str(item.quantity)))

        previous_status = reservation.reservation_status
        reservation = ReservationRepository.update(reservation, {'reservation_status': ReservationStatus.CONFIRMED})

        ReservationHistoryRepository.log_history(
            reservation=reservation,
            previous_status=previous_status,
            new_status=ReservationStatus.CONFIRMED,
            changed_by=user,
            remarks="Reservation confirmed. Stock reserved."
        )

        reservation_confirmed.send(sender=ReservationService, reservation=reservation)
        return reservation

    @staticmethod
    @transaction.atomic
    # Method: cancel_reservation
    def cancel_reservation(reservation_id: str, user=None, remarks="User cancelled.") -> Reservation:
        reservation = ReservationRepository.get_by_id_for_update(reservation_id)
        if not reservation:
            raise ValidationError("Reservation not found.")

        validate_reservation_modifiable(reservation)
        previous_status = reservation.reservation_status

        # If it was confirmed, release the stock
        if previous_status == ReservationStatus.CONFIRMED:
            for item in reservation.items.all():
                inventory = Inventory.objects.filter(
                    product_id=item.product_id, 
                    branch_id=reservation.branch_id
                ).first()
                if inventory:
                    InventoryService.release_stock(str(inventory.id), Decimal(str(item.quantity)))

        reservation = ReservationRepository.update(reservation, {'reservation_status': ReservationStatus.CANCELLED})

        ReservationHistoryRepository.log_history(
            reservation=reservation,
            previous_status=previous_status,
            new_status=ReservationStatus.CANCELLED,
            changed_by=user,
            remarks=remarks
        )

        reservation_cancelled.send(sender=ReservationService, reservation=reservation)
        return reservation

    @staticmethod
    @transaction.atomic
    # Method: modify_reservation
    def modify_reservation(reservation_id: str, updates: Dict[str, Any], items_data: List[Dict[str, Any]] = None, user=None) -> Reservation:
        reservation = ReservationRepository.get_by_id_for_update(reservation_id)
        if not reservation:
            raise ValidationError("Reservation not found.")

        validate_reservation_modifiable(reservation)

        # Re-evaluating items implies releasing old stock if confirmed, and reserving new stock
        if items_data is not None:
            if reservation.reservation_status == ReservationStatus.CONFIRMED:
                # Release old
                for item in reservation.items.all():
                    inv = Inventory.objects.filter(product_id=item.product_id, branch_id=reservation.branch_id).first()
                    if inv:
                        InventoryService.release_stock(str(inv.id), Decimal(str(item.quantity)))
            
            # Clear old and add new
            ReservationItemRepository.clear_items(reservation)
            for item in items_data:
                validate_product_active(item['product'])
            ReservationItemRepository.add_items(reservation, items_data)
            
            if reservation.reservation_status == ReservationStatus.CONFIRMED:
                # Reserve new
                for item in reservation.items.all():
                    inv = Inventory.objects.filter(product_id=item.product_id, branch_id=reservation.branch_id).first()
                    if inv:
                        InventoryService.reserve_stock(str(inv.id), Decimal(str(item.quantity)))

        reservation = ReservationRepository.update(reservation, updates)
        
        ReservationHistoryRepository.log_history(
            reservation=reservation,
            previous_status=reservation.reservation_status,
            new_status=reservation.reservation_status,
            changed_by=user,
            remarks="Reservation modified."
        )

        return reservation

    @staticmethod
    @transaction.atomic
    # Method: convert_to_order
    def convert_to_order(reservation_id: str, user=None) -> Any:
        reservation = ReservationRepository.get_by_id_for_update(reservation_id)
        if not reservation:
            raise ValidationError("Reservation not found.")
            
        if reservation.reservation_status not in [ReservationStatus.PENDING, ReservationStatus.CONFIRMED]:
            raise ValidationError(f"Cannot convert {reservation.reservation_status.lower()} reservation to order.")

        # Release stock if it was confirmed, because OrderService will reserve it again!
        if reservation.reservation_status == ReservationStatus.CONFIRMED:
            for item in reservation.items.all():
                inv = Inventory.objects.filter(product_id=item.product_id, branch_id=reservation.branch_id).first()
                if inv:
                    InventoryService.release_stock(str(inv.id), Decimal(str(item.quantity)))

        # Build payload for OrderService
        order_data = {
            'business': reservation.business,
            'branch': reservation.branch,
            'customer': reservation.customer,
            'order_number': f"ORD-{reservation.reservation_number}",
            'created_by': user,
            'reservation_id': reservation.id
        }
        
        items_payload = []
        for item in reservation.items.all():
            items_payload.append({
                'product': item.product,
                'quantity': item.quantity,
                'unit_price': item.reserved_price
            })

        order = OrderService.create_order(order_data, items_payload)

        # Update reservation status
        previous_status = reservation.reservation_status
        reservation = ReservationRepository.update(reservation, {'reservation_status': ReservationStatus.COMPLETED})

        ReservationHistoryRepository.log_history(
            reservation=reservation,
            previous_status=previous_status,
            new_status=ReservationStatus.COMPLETED,
            changed_by=user,
            remarks=f"Converted to Order {order.order_number}."
        )

        reservation_converted_to_order.send(sender=ReservationService, reservation=reservation, order=order)
        return order

    @staticmethod
    @transaction.atomic
    # Method: expire_stale_reservations
    def expire_stale_reservations():
        """
        Intended to be called by Celery beat or a management command periodically.
        """
        now = timezone.now()
        
        stale_qs = Reservation.objects.filter(
            reservation_status__in=[ReservationStatus.PENDING, ReservationStatus.CONFIRMED],
            is_deleted=False
        )
        
        expired_count = 0
        for reservation in stale_qs:
            # Calculate expiry threshold. E.g., reservation time + expected duration.
            res_datetime = timezone.datetime.combine(reservation.reservation_date, reservation.reservation_time)
            res_datetime = timezone.make_aware(res_datetime)
            expiry_threshold = res_datetime + reservation.expected_duration
            
            if now > expiry_threshold:
                # Expire it
                ReservationService.cancel_reservation(str(reservation.id), remarks="System auto-expired.")
                ReservationRepository.update(reservation, {'reservation_status': ReservationStatus.EXPIRED})
                
                ReservationHistoryRepository.log_history(
                    reservation=reservation,
                    previous_status=ReservationStatus.CANCELLED,
                    new_status=ReservationStatus.EXPIRED,
                    changed_by=None,
                    remarks="Auto-expired due to time threshold."
                )
                reservation_expired.send(sender=ReservationService, reservation=reservation)
                expired_count += 1
                
        return expired_count
