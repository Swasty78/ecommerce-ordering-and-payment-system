from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel
from core.constants import OrderStatus
from products.models import Product

class Order(BaseModel):
    # Order model representing a customer's purchase.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('user')
    )
    shipping_address = models.TextField(
        _('shipping address'),
        blank=True,
        help_text=_('Full shipping address')
    )
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=10, 
        decimal_places=2,
        default=0.00
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"

class OrderItem(BaseModel):
    #OrderItem model representing a specific product within an order.
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('order')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT, 
        related_name='order_items',
        verbose_name=_('product')
    )
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    price = models.DecimalField(
        _('price'),
        max_digits=10, 
        decimal_places=2,
        help_text=_('Price of the product at the time of purchase')
    )
    subtotal = models.DecimalField(
        _('subtotal'),
        max_digits=10, 
        decimal_places=2,
        editable=False
    )

    def save(self, *args, **kwargs):
        # Calculate subtotal before saving
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"
