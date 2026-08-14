import uuid
from django.db import models

# Class: UUIDModel
class UUIDModel(models.Model):
    """
    An abstract base class model that provides a UUID primary key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Class: Meta
    class Meta:
        abstract = True

# Class: TimeStampedModel
class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created_at`` and ``updated_at`` fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Class: Meta
    class Meta:
        abstract = True

# Class: UUIDTimeStampedModel
class UUIDTimeStampedModel(UUIDModel, TimeStampedModel):
    """
    An abstract base class model that provides a UUID primary key and
    self-updating ``created_at`` and ``updated_at`` fields.
    """
    # Class: Meta
    class Meta:
        abstract = True
