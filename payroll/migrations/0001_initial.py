# Generated by Django 3.0 on 2020-06-01 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayrollRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=20)),
                ('month', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Payslip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_nssf', models.IntegerField()),
                ('employer_nssf', models.IntegerField()),
                ('gross_salary', models.IntegerField()),
                ('net_salary', models.IntegerField()),
                ('paye', models.IntegerField()),
                ('total_nssf_contrib', models.IntegerField(default=0)),
                ('overtime', models.IntegerField()),
                ('bonus', models.IntegerField(default=0)),
                ('sacco_deduction', models.IntegerField()),
                ('damage_deduction', models.IntegerField()),
                ('prorate', models.CharField(default='0.0', max_length=20)),
                ('employee', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
                ('payroll_record', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='payroll.PayrollRecord')),
            ],
        ),
    ]
