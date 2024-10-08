# Generated by Django 4.2.4 on 2024-09-18 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerLocationModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('work_area_t', models.CharField(max_length=10, null=True)),
                ('customer_id', models.CharField(max_length=20, null=True)),
                ('latitude', models.FloatField(null=True)),
                ('longitude', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'rdl_customer_location',
                'indexes': [models.Index(fields=['work_area_t'], name='exf_custome_work_ar_3f32a1_idx'), models.Index(fields=['customer_id'], name='exf_custome_custome_4c1d97_idx')],
            },
        ),
    ]
