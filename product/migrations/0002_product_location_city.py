# Generated by Django 4.2.1 on 2023-05-17 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='location_city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
