# Generated by Django 4.0.2 on 2022-04-07 04:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0016_usecoupon_checking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryoffer',
            name='percent',
            field=models.FloatField(default=1, max_length=30, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(90)]),
        ),
        migrations.AlterField(
            model_name='productoffer',
            name='percent',
            field=models.FloatField(default=1, max_length=30, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(90)]),
        ),
    ]
