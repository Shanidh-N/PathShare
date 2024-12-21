# Generated by Django 5.1.3 on 2024-12-18 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rideshare', '0005_alter_all_rides_passenger_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='all_rides',
            name='passenger_details',
        ),
        migrations.AddField(
            model_name='all_rides',
            name='passengers',
            field=models.JSONField(default=dict),
        ),
    ]