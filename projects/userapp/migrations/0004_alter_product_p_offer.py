# Generated by Django 4.0.2 on 2022-03-11 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0003_alter_categorie_c_offer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='p_offer',
            field=models.ForeignKey(blank=True, max_length=30, null=True, on_delete=django.db.models.deletion.SET_NULL, to='userapp.productoffer'),
        ),
    ]
