# Generated by Django 5.1.5 on 2025-06-02 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0026_blogbanner_homecta_pricingcard_productbanner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materialregistration',
            name='mr_sell_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
