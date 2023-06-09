# Generated by Django 4.2.1 on 2023-05-20 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_product_location_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='condition_desc',
            field=models.TextField(blank=True, null=True, verbose_name='condition Description'),
        ),
        migrations.AlterField(
            model_name='productdescription',
            name='description_en',
            field=models.TextField(blank=True, null=True, verbose_name='description EN'),
        ),
        migrations.AlterField(
            model_name='productdescription',
            name='description_jp',
            field=models.TextField(blank=True, null=True, verbose_name='description JP'),
        ),
    ]