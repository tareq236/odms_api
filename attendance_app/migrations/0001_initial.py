# Generated by Django 4.2 on 2023-04-11 22:14

import attendance_app.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_app', '0002_userlist_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_date_time', models.DateTimeField(blank=True, null=True)),
                ('end_date_time', models.DateTimeField(blank=True, null=True)),
                ('late_time_min', models.IntegerField(blank=True, null=True)),
                ('over_time_min', models.IntegerField(blank=True, null=True)),
                ('attendance_type', models.CharField(choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Late', 'Late'), ('Overtime', 'Overtime')], max_length=20, null=True)),
                ('start_latitude', models.DecimalField(decimal_places=16, max_digits=27, null=True)),
                ('start_longitude', models.DecimalField(decimal_places=16, max_digits=27, null=True)),
                ('end_latitude', models.DecimalField(blank=True, decimal_places=16, max_digits=27, null=True)),
                ('end_longitude', models.DecimalField(blank=True, decimal_places=16, max_digits=27, null=True)),
                ('start_image', models.ImageField(blank=True, null=True, upload_to=attendance_app.models.upload_to)),
                ('end_image', models.ImageField(blank=True, null=True, upload_to=attendance_app.models.upload_to)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('sap_id', models.ForeignKey(db_column='sap_id', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='user_app.userlist')),
            ],
            options={
                'verbose_name': 'Attendance',
                'verbose_name_plural': 'Attendance',
                'db_table': 'rdl_attendance',
            },
        ),
    ]
