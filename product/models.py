from django.db import models
from django.utils.translation import gettext_lazy as _

from dry_rest_permissions.generics import authenticated_users

from utils.models import TimeStampModel


class Product(TimeStampModel):
    class Condition(models.TextChoices):
        NEW = 1000
        USED = 3000

    class Country(models.TextChoices):
        JAPAN = 'JP'

    class Status(models.TextChoices):
        DRAFT = 'Draft'
        PUBLISH = 'Publish'
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    item_number = models.CharField(
        _('item Number'),
        max_length=20,
        null=True,
        blank=True
    )
    url = models.URLField(_('url'), null=True, blank=True)
    site = models.CharField(
        _('site'),
        max_length=100,
        null=True,
        blank=True
    )
    title_jp = models.CharField(_('title JP'), max_length=255, null=True, blank=True)
    title_en = models.CharField(_('title EN'), max_length=255, null=True, blank=True)
    item_category = models.IntegerField(
        _('item Category'),
        null=True
    )
    condition = models.CharField(
        _('condition'),
        max_length=20,
        blank=True,
        choices=Condition.choices
    )
    condition_desc = models.TextField(
        _('condition Description'),
        null=True,
        blank=True,
    )
    price_en = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    price_jp = models.IntegerField(
        _('price'),
        null=True,
        blank=True
    )
    quantity = models.IntegerField(
        _('quantity'),
        null=True,
        blank=True
    )
    point = models.IntegerField(
        _('point'),
        null=True
    )
    shipping_policy = models.CharField(
        _('shipping Policy'),
        max_length=100,
        null=True,
        blank=True
    )
    location_country = models.CharField(
        max_length=100,
        default=Country.JAPAN,
        choices=Country.choices
    )
    location_city = models.CharField(
        max_length=255,
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
    created_by = models.ForeignKey(
        "users.user",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    comment = models.TextField(
        _('comment'),
        null=True
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


class ProductPhoto(TimeStampModel):
    product = models.ForeignKey(
        "product.Product", null=True, blank=True, on_delete=models.SET_NULL
    )
    path = models.ImageField(
        _('image file'),
        upload_to="productphoto"
    )
    width = models.DecimalField(
        _('width'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    height = models.DecimalField(
        _('height'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    @authenticated_users
    def has_read_permission(request):
        return True

    @authenticated_users
    def has_write_permission(request):
        return True


class ProductDescription(TimeStampModel):
    product = models.ForeignKey(
        "product.Product", null=True, blank=True, on_delete=models.SET_NULL
    )
    title_jp = models.CharField(
        _('title JP'),
        max_length=250,
        null=True,
        blank=True
    )
    title_en = models.CharField(
        _('title EN'),
        max_length=250,
        null=True,
        blank=True
    )
    description_jp = models.TextField(
        _('description JP'),
        null=True,
        blank=True
    )
    description_en = models.TextField(
        _('description EN'),
        null=True,
        blank=True
    )
