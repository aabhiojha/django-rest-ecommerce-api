from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class SEOMixin(models.Model):
    meta_field = models.CharField(max_length=60, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)

    class Meta:
        abstract = True
