# Generated by Django 5.1.5 on 2025-06-03 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0032_materialinventorydetail_id_debit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('0', 'Pending'), ('1', 'Approved'), ('2', 'Processing'), ('3', 'Completed'), ('4', 'Cancelled')], default='pending', max_length=20),
        ),
    ]
