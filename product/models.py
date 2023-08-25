from django.db import models
from django.utils.translation import gettext_lazy as _

from dry_rest_permissions.generics import authenticated_users


class Product(models.Model):
    created_at = models.CharField(
        _('created at'),
        max_length=30
    )
    updated_at = models.CharField(
        _('updated at'),
        max_length=30,
        null=True,
        blank=True
    )
    product_name = models.CharField(
        _('product_name'),
        max_length=255
    )
    ec_site = models.CharField(
        _('ec_site'),
        max_length=50
    )
    purchase_url = models.CharField(
        _('purchase_url'),
        max_length=500
    )
    ebay_url = models.CharField(
        _('ebay_url'),
        max_length=500
    )
    purchase_price = models.DecimalField(
        _('purchase_price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    sell_price_en = models.DecimalField(
        _('sell_price_en'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    profit = models.DecimalField(
        _('profit'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    profit_rate = models.DecimalField(
        _('profit rate'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    prima = models.DecimalField(
        _('prima'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    shipping = models.DecimalField(
        _('export shipping fee'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    quantity = models.IntegerField(
        _('quantity'),
        null=True
    )
    notes = models.CharField(
        _('notes'),
        max_length = 3000,
        null = True,
        blank = True
    )
    created_by = models.ForeignKey(
        "users.User", 
        null = True,
        blank=True,
        on_delete = models.SET_NULL
    )

    @authenticated_users
    def has_read_permission(request):
        return True

    @authenticated_users
    def has_write_permission(request):
        return True

    @authenticated_users
    def has_scrape_data_permission(request):
        return True

class OrderList(models.Model):
    created_at = models.CharField(
        _('created at'),
        max_length=30
    )
    updated_at = models.CharField(
        _('updated at'),
        max_length=30,
        null=True,
        blank=True
    )
    product_name = models.CharField(
        _('product_name'),
        max_length=255
    )
    ec_site = models.CharField(
        _('ec_site'),
        max_length=50
    )
    purchase_url = models.CharField(
        _('purchase_url'),
        max_length=500
    )
    ebay_url = models.CharField(
        _('ebay_url'),
        max_length=500
    )
    purchase_price = models.DecimalField(
        _('purchase_price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    sell_price_en = models.DecimalField(
        _('sell_price_en'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    profit = models.DecimalField(
        _('profit'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    profit_rate = models.DecimalField(
        _('profit rate'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    prima = models.DecimalField(
        _('prima'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    shipping = models.DecimalField(
        _('export shipping fee'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    quantity = models.IntegerField(
        _('quantity'),
        null=True
    )
    order_num = models.CharField(
        _('order_num'),
        max_length=50
    )
    ordered_at = models.CharField(
        _('ordered_at'),
        max_length = 30
    )
    notes = models.CharField(
        _('notes'),
        max_length = 3000,
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete = models.CASCADE
    )

    @authenticated_users
    def has_read_permission(request):
        return True

    @authenticated_users
    def has_write_permission(request):
        return True

    @authenticated_users
    def has_scrape_data_permission(request):
        return True

class DeletedList(models.Model):

    created_at = models.CharField(
        _('created at'),
        max_length=30
    )
    updated_at = models.CharField(
        _('updated at'),
        max_length=30,
        null=True,
        blank=True
    )
    product_name = models.CharField(
        _('product_name'),
        max_length=255
    )
    ec_site = models.CharField(
        _('ec_site'),
        max_length=50
    )
    purchase_url = models.CharField(
        _('purchase_url'),
        max_length=500
    )
    ebay_url = models.CharField(
        _('ebay_url'),
        max_length=500
    )
    purchase_price = models.DecimalField(
        _('purchase_price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    sell_price_en = models.DecimalField(
        _('sell_price_en'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    profit = models.DecimalField(
        _('profit'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    profit_rate = models.DecimalField(
        _('profit rate'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    prima = models.DecimalField(
        _('prima'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    shipping = models.DecimalField(
        _('export shipping fee'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    quantity = models.IntegerField(
        _('quantity'),
        null=True
    )
    notes = models.CharField(
        _('notes'),
        max_length = 3000,
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete = models.CASCADE
    )
    deleted_at = models.CharField(
        "deleted date",
        max_length = 64
    )

    @authenticated_users
    def has_read_permission(request):
        return True

    @authenticated_users
    def has_write_permission(request):
        return True

    @authenticated_users
    def has_scrape_data_permission(request):
        return True
    
class MailList(models.Model):

    product_id = models.CharField(
        _('product id'),
        max_length=64
    )