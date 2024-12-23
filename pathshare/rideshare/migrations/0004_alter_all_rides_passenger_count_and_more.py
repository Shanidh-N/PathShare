# Generated by Django 5.1.3 on 2024-12-17 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rideshare', '0003_all_rides_shared_alter_all_rides_vehicle_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='all_rides',
            name='passenger_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='all_rides',
            name='total_cost',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='all_rides',
            name='total_distance',
            field=models.FloatField(default=0),
        ),
    ]
