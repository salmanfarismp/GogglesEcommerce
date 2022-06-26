# Generated by Django 4.0.2 on 2022-03-11 11:57

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=70)),
            ],
        ),
        migrations.CreateModel(
            name='CategoryOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('percent', models.FloatField(default=0, max_length=30, null=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CouponDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30, null=True)),
                ('code', models.CharField(max_length=30)),
                ('offer_percentage', models.FloatField(default=0, max_length=30)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('exp_date', models.DateField(blank=True, null=True)),
                ('use_count', models.FloatField(default=0, max_length=30)),
                ('total_lessed_money', models.FloatField(default=0, max_length=30)),
                ('active', models.BooleanField(default=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('percent', models.FloatField(default=0, max_length=30, null=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Referal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='UseCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('used', models.BooleanField(default=False)),
                ('lessed_money', models.FloatField(default=0, max_length=30)),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='userapp.coupondetail')),
            ],
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='Payment_method',
            new_name='payment_method',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='Payment_status',
            new_name='payment_status',
        ),
        migrations.RemoveField(
            model_name='product',
            name='offer',
        ),
        migrations.AddField(
            model_name='categorie',
            name='category_img',
            field=models.ImageField(blank=True, null=True, upload_to='product_images'),
        ),
        migrations.AddField(
            model_name='categorie',
            name='footer',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='device',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='order_count',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='ref_code',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='coupon_used',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='order_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(max_length=17, null=True, validators=[django.core.validators.RegexValidator(message='Invalid Phone Number', regex='^1?\\d{9,15}$')]),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='order_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='order_status',
            field=models.CharField(choices=[('Cart', 'Cart'), ('Gobuy', 'Gobuy'), ('Placed', 'Placed'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled'), ('Cancellation Requested', 'Cancellation Requested'), ('Failed', 'Failed'), ('Shipped', 'Shipped'), ('Out Of Delevery', 'Out Of Delevery'), ('Return', 'Return')], default='Processing', max_length=30),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='item_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='payment',
            name='total_amount',
            field=models.FloatField(default=0, max_length=30),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_name',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_price',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='quantity_available',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='Offer',
        ),
        migrations.AddField(
            model_name='usecoupon',
            name='fororder',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='userapp.orderdetail'),
        ),
        migrations.AddField(
            model_name='usecoupon',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='referal',
            name='recommended_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ref_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='referal',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='banner',
            name='related_coupon',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='userapp.coupondetail'),
        ),
        migrations.AddField(
            model_name='categorie',
            name='c_offer',
            field=models.ForeignKey(default=0, max_length=30, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='userapp.categoryoffer'),
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='userapp.brand'),
        ),
        migrations.AddField(
            model_name='product',
            name='p_offer',
            field=models.ForeignKey(default=0, max_length=30, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='userapp.productoffer'),
        ),
    ]