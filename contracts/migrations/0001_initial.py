# Generated by Django 3.0 on 2020-01-27 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0005_auto_20200127_1626'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_number', models.IntegerField(unique=True)),
                ('effective_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('status', models.DateField()),
                ('Risk', models.CharField(max_length=10)),
                ('document', models.FileField(upload_to='')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Position')),
            ],
        ),
    ]