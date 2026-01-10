from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel

class Category(BaseModel):
    
    #Category model for grouping products.
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name=_('parent category')
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name

class Product(BaseModel):
    
    # Product model representing items for sale.
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')

    name = models.CharField(_('name'), max_length=255)
    sku = models.CharField(_('SKU'), max_length=100, unique=True, db_index=True)
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(_('stock'), default=0)
    status = models.CharField(
        _('status'), 
        max_length=20, 
        choices=Status.choices, 
        default=Status.ACTIVE
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products',
        verbose_name=_('category')
    )

    def __str__(self):
        return f"{self.name} ({self.sku})"
