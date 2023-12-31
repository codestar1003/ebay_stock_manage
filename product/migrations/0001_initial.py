# Generated by Django 4.2.1 on 2023-08-17 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.CharField(max_length=30, verbose_name='created at')),
                ('updated_at', models.CharField(blank=True, max_length=30, null=True, verbose_name='updated at')),
                ('product_name', models.CharField(max_length=255, verbose_name='product_name')),
                ('ec_site', models.CharField(max_length=50, verbose_name='ec_site')),
                ('purchase_url', models.CharField(max_length=500, verbose_name='purchase_url')),
                ('ebay_url', models.CharField(max_length=500, verbose_name='ebay_url')),
                ('purchase_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='purchase_price')),
                ('sell_price_en', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='sell_price_en')),
                ('profit', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='profit')),
                ('profit_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='profit rate')),
                ('prima', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='prima')),
                ('shipping', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='export shipping fee')),
                ('quantity', models.IntegerField(null=True, verbose_name='quantity')),
                ('notes', models.CharField(blank=True, max_length=3000, null=True, verbose_name='notes')),
                ('deleted_at', models.CharField(max_length=64, verbose_name='deleted date')),
            ],
        ),
        migrations.CreateModel(
            name='MailList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(max_length=64, verbose_name='product id')),
            ],
        ),
        migrations.CreateModel(
            name='OrderList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.CharField(max_length=30, verbose_name='created at')),
                ('updated_at', models.CharField(blank=True, max_length=30, null=True, verbose_name='updated at')),
                ('product_name', models.CharField(max_length=255, verbose_name='product_name')),
                ('ec_site', models.CharField(max_length=50, verbose_name='ec_site')),
                ('purchase_url', models.CharField(max_length=500, verbose_name='purchase_url')),
                ('ebay_url', models.CharField(max_length=500, verbose_name='ebay_url')),
                ('purchase_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='purchase_price')),
                ('sell_price_en', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='sell_price_en')),
                ('profit', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='profit')),
                ('profit_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='profit rate')),
                ('prima', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='prima')),
                ('shipping', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='export shipping fee')),
                ('quantity', models.IntegerField(null=True, verbose_name='quantity')),
                ('order_num', models.CharField(max_length=50, verbose_name='order_num')),
                ('ordered_at', models.CharField(max_length=30, verbose_name='ordered_at')),
                ('notes', models.CharField(blank=True, max_length=3000, null=True, verbose_name='notes')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.CharField(max_length=30, verbose_name='created at')),
                ('updated_at', models.CharField(blank=True, max_length=30, null=True, verbose_name='updated at')),
                ('product_name', models.CharField(max_length=255, verbose_name='product_name')),
                ('ec_site', models.CharField(max_length=50, verbose_name='ec_site')),
                ('purchase_url', models.CharField(max_length=500, verbose_name='purchase_url')),
                ('ebay_url', models.CharField(max_length=500, verbose_name='ebay_url')),
                ('purchase_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='purchase_price')),
                ('sell_price_en', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='sell_price_en')),
                ('profit', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='profit')),
                ('profit_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='profit rate')),
                ('prima', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='prima')),
                ('shipping', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='export shipping fee')),
                ('quantity', models.IntegerField(null=True, verbose_name='quantity')),
                ('notes', models.CharField(blank=True, max_length=3000, null=True, verbose_name='notes')),
            ],
        ),
    ]
