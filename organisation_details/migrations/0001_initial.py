# Generated by Django 2.2.3 on 2020-05-04 01:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('status', models.CharField(default='Active', max_length=15)),
                ('hod', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('status', models.CharField(default='Active', max_length=15)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organisation_details.Department')),
                ('supervisors', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('number_of_slots', models.IntegerField()),
                ('type', models.CharField(default='Full Time', max_length=20)),
                ('salary', models.IntegerField(default=0)),
                ('description', models.TextField(blank=True)),
                ('currency', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='settings.Currency')),
            ],
        ),
        migrations.CreateModel(
            name='OrganisationDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='organisation_details.Department')),
                ('employee', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
                ('position', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='organisation_details.Position')),
                ('team', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='organisation_details.Team')),
            ],
        ),
    ]
