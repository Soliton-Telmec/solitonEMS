# Generated by Django 3.0 on 2020-02-17 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ems_admin', '0003_audittrail'),
    ]

    operations = [
        migrations.RenameField(
            model_name='audittrail',
            old_name='created_at',
            new_name='created',
        ),
    ]