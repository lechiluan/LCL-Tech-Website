# Generated by Django 4.1.7 on 2023-04-01 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_rename_amount_cartitem_sub_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True),
        ),
    ]