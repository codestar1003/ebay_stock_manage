# Generated by Django 4.2.1 on 2023-06-16 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_product_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='item_number',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=20, null=True, verbose_name='item Number'),
        ),
    ]