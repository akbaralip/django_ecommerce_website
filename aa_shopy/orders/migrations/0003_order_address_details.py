# Generated by Django 4.2.3 on 2023-08-01 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_razor_pay_order_id_order_razor_pay_payment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address_details',
            field=models.TextField(blank=True),
        ),
    ]