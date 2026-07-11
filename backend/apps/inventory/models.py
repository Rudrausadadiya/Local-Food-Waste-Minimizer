import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from common.models import UUIDTimeStampedModel
from apps.business.models import Business, Branch
from apps.products.models import Product

class Supplier(UUIDTimeStampedModel):
    """Supplier for inventory batches and future purchase orders."""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='suppliers')
    supplier_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.supplier_name


class Inventory(UUIDTimeStampedModel):
    """Main inventory tracking model per business, branch, and product."""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='inventories')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='inventories')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    damaged_stock = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    expired_stock = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    reserved_stock = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    maximum_stock = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    average_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    last_stock_update = models.DateTimeField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Inventories'
        unique_together = ('business', 'branch', 'product')
        indexes = [
            models.Index(fields=['business', 'branch', 'product']),
        ]

    @property
    def available_stock(self) -> Decimal:
        """Returns stock available for sale/transfer."""
        return self.current_stock - self.damaged_stock - self.expired_stock - self.reserved_stock

    def clean(self):
        if self.current_stock < Decimal('0.00'):
            raise ValidationError(_('Stock cannot become negative.'))
        if self.reserved_stock > self.current_stock - self.damaged_stock - self.expired_stock:
            raise ValidationError(_('Cannot reserve more stock than available.'))
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_name} at {self.branch.branch_name}"


class StockTransaction(UUIDTimeStampedModel):
    """Audit trail for every stock movement."""
    class TransactionType(models.TextChoices):
        STOCK_IN = 'STOCK_IN', _('Stock In')
        STOCK_OUT = 'STOCK_OUT', _('Stock Out')
        TRANSFER = 'TRANSFER', _('Transfer')
        ADJUSTMENT = 'ADJUSTMENT', _('Adjustment')
        WASTE = 'WASTE', _('Waste')

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=100, blank=True, null=True, help_text=_("e.g. PO number, Transfer ID"))
    
    source = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_transactions_out')
    destination = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_transactions_in')
    
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='stock_transactions')

    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.quantity} for {self.inventory.product.product_name}"


class InventoryBatch(UUIDTimeStampedModel):
    """Batch tracking for FIFO, expiry, and cost."""
    class BatchStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        EXPIRED = 'EXPIRED', _('Expired')
        DEPLETED = 'DEPLETED', _('Depleted')
        RECALLED = 'RECALLED', _('Recalled')

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=100)
    manufacturing_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='batches')
    status = models.CharField(max_length=20, choices=BatchStatus.choices, default=BatchStatus.ACTIVE)
    
    received_date = models.DateField(default=timezone.now)
    supplier_invoice_number = models.CharField(max_length=100, blank=True, null=True)
    storage_location = models.CharField(max_length=100, blank=True, null=True, help_text=_("e.g. Aisle 5, Shelf B"))

    class Meta:
        verbose_name_plural = 'Inventory Batches'
        unique_together = ('inventory', 'batch_number')
        
    def clean(self):
        if self.expiry_date and self.expiry_date < timezone.now().date():
            raise ValidationError(_("Cannot receive expired inventory."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Batch {self.batch_number} - {self.inventory.product.product_name}"


class WasteRecord(UUIDTimeStampedModel):
    """Records for damaged or expired inventory items."""
    class WasteReason(models.TextChoices):
        EXPIRED = 'EXPIRED', _('Expired')
        DAMAGED = 'DAMAGED', _('Damaged')
        SPOILAGE = 'SPOILAGE', _('Spoilage')
        THEFT = 'THEFT', _('Theft')
        OTHER = 'OTHER', _('Other')

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='waste_records')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    waste_reason = models.CharField(max_length=20, choices=WasteReason.choices)
    
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_wastes')
    image = models.URLField(blank=True, null=True, help_text=_("Evidence of waste"))
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_waste_reason_display()} - {self.quantity} of {self.inventory.product.product_name}"
