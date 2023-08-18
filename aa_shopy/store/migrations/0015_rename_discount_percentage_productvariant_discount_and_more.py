# Generated by Django 4.2.3 on 2023-08-02 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_alter_productvariant_discount_percentage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productvariant',
            old_name='discount_percentage',
            new_name='discount',
        ),
        migrations.AddField(
            model_name='productvariant',
            name='discount_price',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
    ]