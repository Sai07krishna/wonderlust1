# Generated by Django 5.2.1 on 2025-05-14 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0003_package_packageimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=10),
        ),
    ]
