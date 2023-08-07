# Generated by Django 4.2.1 on 2023-06-28 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='app_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='app Id'),
        ),
        migrations.AddField(
            model_name='user',
            name='cert_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='cert Id'),
        ),
        migrations.AddField(
            model_name='user',
            name='dev_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='dev Id'),
        ),
        migrations.AddField(
            model_name='user',
            name='ebay_token',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='ebay Token'),
        ),
    ]