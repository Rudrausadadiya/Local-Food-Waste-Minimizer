from rest_framework import serializers
from .models import Table, Reservation, ReservationItem, ReservationTable, ReservationHistory
from .services import ReservationService

# Class: TableSerializer
class TableSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = Table
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

# Class: ReservationItemSerializer
class ReservationItemSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = ReservationItem
        fields = ['id', 'product', 'quantity', 'reserved_price']
        read_only_fields = ('id',)

# Class: ReservationTableSerializer
class ReservationTableSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = ReservationTable
        fields = ['id', 'table']
        read_only_fields = ('id',)

# Class: ReservationHistorySerializer
class ReservationHistorySerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = ReservationHistory
        fields = '__all__'
        read_only_fields = ('id', 'reservation', 'previous_status', 'new_status', 'changed_by', 'remarks', 'changed_at')

# Class: ReservationReadSerializer
class ReservationReadSerializer(serializers.ModelSerializer):
    items = ReservationItemSerializer(many=True, read_only=True)
    reserved_tables = ReservationTableSerializer(many=True, read_only=True)
    history = ReservationHistorySerializer(many=True, read_only=True)
    
    # Class: Meta
    class Meta:
        model = Reservation
        fields = '__all__'

# Class: ReservationWriteSerializer
class ReservationWriteSerializer(serializers.ModelSerializer):
    items = ReservationItemSerializer(many=True, write_only=True, required=False)
    reserved_tables = ReservationTableSerializer(many=True, write_only=True, required=False)
    
    # Class: Meta
    class Meta:
        model = Reservation
        fields = [
            'business', 'branch', 'customer', 'reservation_number', 'reservation_type',
            'reservation_date', 'reservation_time', 'expected_duration', 'party_size',
            'advance_amount', 'advance_payment_status', 'reservation_source',
            'expected_arrival', 'actual_arrival', 'no_show', 'notes', 'items', 'reserved_tables'
        ]

    # Method: create
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        tables_data = validated_data.pop('reserved_tables', [])
        user = self.context['request'].user if 'request' in self.context else None
        
        validated_data['created_by'] = user
        return ReservationService.create_reservation(validated_data, items_data, tables_data, user)

    # Method: update
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        validated_data.pop('reserved_tables', None) # We'll skip table modifications in this simple update
        user = self.context['request'].user if 'request' in self.context else None
        
        return ReservationService.modify_reservation(str(instance.id), validated_data, items_data, user)
