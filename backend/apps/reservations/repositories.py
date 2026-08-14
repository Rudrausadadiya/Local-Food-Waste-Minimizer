from typing import Optional, List, Dict, Any
from django.db.models import QuerySet
from .models import Table, Reservation, ReservationItem, ReservationTable, ReservationHistory

# Class: TableRepository
class TableRepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(table_id: str) -> Optional[Table]:
        return Table.objects.filter(id=table_id, is_active=True).first()
        
    @staticmethod
    # Method: get_active_by_branch
    def get_active_by_branch(branch_id: str) -> QuerySet:
        return Table.objects.filter(branch_id=branch_id, is_active=True)

# Class: ReservationRepository
class ReservationRepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(reservation_id: str) -> Optional[Reservation]:
        return Reservation.objects.filter(id=reservation_id, is_deleted=False).first()

    @staticmethod
    # Method: get_by_id_for_update
    def get_by_id_for_update(reservation_id: str) -> Optional[Reservation]:
        return Reservation.objects.select_for_update().filter(id=reservation_id, is_deleted=False).first()
        
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> Reservation:
        return Reservation.objects.create(**data)
        
    @staticmethod
    # Method: update
    def update(reservation: Reservation, data: Dict[str, Any]) -> Reservation:
        for key, value in data.items():
            setattr(reservation, key, value)
        reservation.save()
        return reservation

    @staticmethod
    # Method: soft_delete
    def soft_delete(reservation: Reservation) -> None:
        reservation.is_deleted = True
        reservation.save(update_fields=['is_deleted', 'updated_at'])
        
    @staticmethod
    # Method: get_stale_reservations
    def get_stale_reservations(expiry_time) -> QuerySet:
        return Reservation.objects.filter(
            reservation_status__in=['PENDING', 'CONFIRMED'],
            is_deleted=False,
            reservation_date__lt=expiry_time.date()
        ) | Reservation.objects.filter(
            reservation_status__in=['PENDING', 'CONFIRMED'],
            is_deleted=False,
            reservation_date=expiry_time.date(),
            reservation_time__lt=expiry_time.time()
        )

# Class: ReservationItemRepository
class ReservationItemRepository:
    @staticmethod
    # Method: add_items
    def add_items(reservation: Reservation, items_data: List[Dict[str, Any]]) -> List[ReservationItem]:
        items = [ReservationItem(reservation=reservation, **item_data) for item_data in items_data]
        return ReservationItem.objects.bulk_create(items)
        
    @staticmethod
    # Method: clear_items
    def clear_items(reservation: Reservation) -> None:
        ReservationItem.objects.filter(reservation=reservation).delete()

# Class: ReservationTableRepository
class ReservationTableRepository:
    @staticmethod
    # Method: add_tables
    def add_tables(reservation: Reservation, tables_data: List[Dict[str, Any]]) -> List[ReservationTable]:
        tables = [ReservationTable(reservation=reservation, **table_data) for table_data in tables_data]
        return ReservationTable.objects.bulk_create(tables)
        
    @staticmethod
    # Method: clear_tables
    def clear_tables(reservation: Reservation) -> None:
        ReservationTable.objects.filter(reservation=reservation).delete()
        
    @staticmethod
    # Method: check_overlap
    def check_overlap(table_ids: List[str], res_date, res_start_time, res_end_time, exclude_res_id=None) -> bool:
        from datetime import datetime
        
        # This is a simplified overlap check.
        # It finds any active reservation for these tables on the same date.
        # Then we verify time overlap in Python or via complex Q objects.
        # For a robust approach, we need to check if the existing reservations overlap with [res_start, res_end].
        
        qs = ReservationTable.objects.filter(
            table_id__in=table_ids,
            reservation__reservation_date=res_date,
            reservation__reservation_status__in=['PENDING', 'CONFIRMED'],
            reservation__is_deleted=False
        )
        if exclude_res_id:
            qs = qs.exclude(reservation_id=exclude_res_id)
            
        for rt in qs:
            existing_start = rt.reservation.reservation_time
            # Calculate end time using expected_duration
            existing_start_dt = datetime.combine(res_date, existing_start)
            existing_end_dt = existing_start_dt + rt.reservation.expected_duration
            
            res_start_dt = datetime.combine(res_date, res_start_time)
            res_end_dt = res_start_dt + res_end_time
            
            if max(existing_start_dt, res_start_dt) < min(existing_end_dt, res_end_dt):
                return True
        return False

# Class: ReservationHistoryRepository
class ReservationHistoryRepository:
    @staticmethod
    # Method: log_history
    def log_history(reservation: Reservation, previous_status: str, new_status: str, changed_by, remarks: str = "") -> ReservationHistory:
        return ReservationHistory.objects.create(
            reservation=reservation,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            remarks=remarks
        )
