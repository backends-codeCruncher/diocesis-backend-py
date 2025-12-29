import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    deletedAt = models.DateTimeField(null=True, blank=True)
    updatedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by",
        on_delete=models.SET_NULL
    )
    deletedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted_by",
        on_delete=models.SET_NULL
    )

    class Meta:
        abstract = True


    def is_active(self):
        return self.isActive