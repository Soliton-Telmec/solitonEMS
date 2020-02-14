# Generated by Django 3.0 on 2020-02-03 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
        ('training', '0002_auto_20200203_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='currency',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='settings.Currency'),
            preserve_default=False,
        ),
    ]