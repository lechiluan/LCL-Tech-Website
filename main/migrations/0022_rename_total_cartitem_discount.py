# Generated by Django 4.1.7 on 2023-04-01 06:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_alter_coupon_discount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='total',
            new_name='discount',
        ),
    ]
