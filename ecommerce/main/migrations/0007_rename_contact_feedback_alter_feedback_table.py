# Generated by Django 4.1.7 on 2023-03-27 05:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_product_sold'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Contact',
            new_name='Feedback',
        ),
        migrations.AlterModelTable(
            name='feedback',
            table='Feedback',
        ),
    ]