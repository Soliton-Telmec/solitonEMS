# Generated by Django 3.0.7 on 2020-09-28 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0004_deduction_police_fine'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='local_service_tax',
            field=models.IntegerField(default=0),
        ),
    ]
