# Generated by Django 4.2.3 on 2023-07-14 09:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_rename_gname_gender_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='banner_image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.bannerimage'),
        ),
    ]
