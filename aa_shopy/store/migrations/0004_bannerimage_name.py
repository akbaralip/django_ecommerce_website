# Generated by Django 4.2.3 on 2023-07-14 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_category_banner_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='bannerimage',
            name='name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
