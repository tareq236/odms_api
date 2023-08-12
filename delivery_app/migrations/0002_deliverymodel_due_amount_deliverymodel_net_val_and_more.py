# Generated by Django 4.2 on 2023-08-12 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverymodel',
            name='due_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='deliverymodel',
            name='net_val',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='deliverymodel',
            name='cash_collection',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, null=True),
        ),
    ]