# Generated by Django 5.2.1 on 2025-05-20 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0008_package_expiry_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='views_count',
            field=models.IntegerField(default=0),
        ),
    ]
