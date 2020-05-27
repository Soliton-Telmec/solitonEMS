# Generated by Django 3.0 on 2020-05-27 00:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('basic_salary', models.IntegerField(default=1000000)),
                ('grade', models.CharField(default='', max_length=3)),
                ('gender', models.CharField(max_length=10)),
                ('start_date', models.DateField()),
                ('marital_status', models.CharField(max_length=10)),
                ('dob', models.DateField()),
                ('nationality', models.CharField(max_length=20)),
                ('nssf_no', models.CharField(max_length=20)),
                ('telephone_no', models.CharField(max_length=20)),
                ('residence_address', models.CharField(max_length=20)),
                ('national_id', models.CharField(max_length=20)),
                ('ura_tin', models.CharField(max_length=20)),
                ('annual_allowance', models.IntegerField(default=21)),
                ('leave_balance', models.IntegerField(default=21)),
                ('balance_last_year', models.IntegerField(default=0)),
                ('leave_status', models.CharField(default='At Work', max_length=45)),
                ('image_url', models.CharField(default='', max_length=20)),
                ('status', models.CharField(default='Active', max_length=20)),
                ('title', models.CharField(blank=True, max_length=10)),
                ('work_station', models.CharField(blank=True, max_length=20)),
                ('lunch_allowance', models.IntegerField(default=0)),
                ('currency', models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='settings.Currency')),
            ],
        ),
        migrations.CreateModel(
            name='HomeAddress',
            fields=[
                ('employee', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='employees.Employee')),
                ('district', models.CharField(max_length=20)),
                ('division', models.CharField(max_length=20)),
                ('county', models.CharField(max_length=20)),
                ('sub_county', models.CharField(max_length=20)),
                ('parish', models.CharField(max_length=20)),
                ('village', models.CharField(max_length=20)),
                ('address', models.CharField(max_length=20)),
                ('telephone', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Supervision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supervisee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervisors', to='employees.Employee')),
                ('supervisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervisees', to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Spouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('national_id', models.CharField(max_length=40)),
                ('dob', models.DateField()),
                ('occupation', models.CharField(max_length=40)),
                ('telephone', models.CharField(max_length=40)),
                ('nationality', models.CharField(max_length=40)),
                ('passport_number', models.CharField(max_length=40)),
                ('alien_certificate_number', models.CharField(max_length=40)),
                ('immigration_file_number', models.CharField(max_length=40)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Leave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.CharField(max_length=20)),
                ('nin', models.CharField(max_length=30)),
                ('department', models.CharField(max_length=15)),
                ('apply_date', models.DateField()),
                ('_year', models.CharField(max_length=4)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('supervisor', models.CharField(max_length=45)),
                ('sup_Status', models.CharField(max_length=15)),
                ('hod', models.CharField(max_length=45)),
                ('hod_status', models.CharField(max_length=15)),
                ('Employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='EmergencyContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('relationship', models.CharField(max_length=40)),
                ('mobile_number', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=40)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Dependant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('dob', models.DateField()),
                ('gender', models.CharField(default='', max_length=40)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Deduction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('amount', models.IntegerField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Certification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('year_completed', models.CharField(max_length=4)),
                ('grade', models.CharField(max_length=20)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Beneficiary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('relationship', models.CharField(max_length=40)),
                ('mobile_number', models.CharField(max_length=40)),
                ('percentage', models.CharField(max_length=40)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='BankDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_of_bank', models.CharField(max_length=20)),
                ('branch', models.CharField(max_length=20)),
                ('bank_account', models.CharField(max_length=20)),
                ('employee', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Allowance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('amount', models.IntegerField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
    ]
