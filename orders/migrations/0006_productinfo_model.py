# Generated by Django 4.2 on 2023-06-11 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_customuser_is_active_alter_customuser_is_staff_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productinfo',
            name='model',
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
