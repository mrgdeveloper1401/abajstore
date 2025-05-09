# Generated by Django 5.1.8 on 2025-04-26 05:49

import django.db.models.deletion
import django.utils.timezone
import django_jalali.db.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=30, unique=True, verbose_name='کد')),
                ('value', models.PositiveSmallIntegerField(help_text='مقدار تخفیف به درصد', verbose_name='مقدار')),
                ('valid_until', models.DateField(verbose_name='معتبر تا تاریخ')),
                ('active', models.BooleanField(default=True, verbose_name='فعال')),
            ],
            options={
                'verbose_name': 'کد تخفیف',
                'verbose_name_plural': 'کد تخفیف',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank', models.CharField(blank=True, choices=[('پارسیان', 'پارسیان'), ('ملت', 'ملت')], max_length=10, null=True, verbose_name='درگاه')),
                ('token', models.CharField(max_length=255, verbose_name='شناسه پرداخت')),
                ('rrn', models.CharField(blank=True, max_length=50, null=True, verbose_name='شماره مرجع')),
                ('terminal_no', models.CharField(blank=True, max_length=50, null=True, verbose_name='شماره ترمینال')),
                ('amount', models.CharField(default=0, max_length=20, verbose_name='مبلغ')),
                ('hash_card_no', models.CharField(default=0, max_length=100, verbose_name='شماره کارت (هش شده)')),
                ('response_code', models.CharField(default=0, max_length=100, verbose_name='کد پاسخ سرور')),
                ('response', models.JSONField(default=dict, verbose_name='پاسخ سرور')),
                ('status', models.CharField(choices=[('در انتظار پرداخت', 'در انتظار پرداخت'), ('پرداخت موفق', 'پرداخت موفق'), ('پرداخت ناموفق', 'پرداخت ناموفق')], default='در انتظار پرداخت', max_length=30, verbose_name='وضعیت')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='تاریخ آپدیت')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=15, unique=True, verbose_name='کد سفارش')),
                ('time_slot', models.IntegerField(choices=[(1, '08:00 - 10:00'), (2, '10:00 - 12:00'), (3, '12:00 - 14:00'), (4, '14:00 - 16:00'), (5, '16:00 - 18:00'), (6, '18:00 - 20:00'), (7, '20:00 - 22:00'), (8, '22:00 - 24:00')], db_index=True, verbose_name='بازه زمانی')),
                ('delivery_date', models.DateField(default=django.utils.timezone.now, verbose_name='تاریخ ارسال')),
                ('delivery_type', models.CharField(choices=[('ارسال زماندار', 'ارسال زماندار'), ('ارسال فوری', 'ارسال فوری')], default='ارسال زماندار', max_length=20, verbose_name='نوع ارسال')),
                ('send_price', models.PositiveIntegerField(default=0, help_text='به تومان', verbose_name='هزینه ی ارسال')),
                ('status', models.CharField(choices=[('در انتظار پرداخت', 'در انتظار پرداخت'), ('پرداخت درب منزل', 'پرداخت درب منزل'), ('پرداخت شده', 'پرداخت شده'), ('ارسال شده', 'ارسال شده'), ('تحویل داده شده', 'تحویل داده شده'), ('لغو شده', 'لغو شده')], default='در انتظار پرداخت', max_length=20, verbose_name='وضعیت')),
                ('rrn', models.CharField(blank=True, help_text='شماره یکتایی که بانک بعد از اتمام موفق تراکنش، همراه با شماره درخواست به پذیرنده میدهد. این شماره جهت پیگیریهای مالی استفاده میگردد.', max_length=50, null=True, verbose_name='شماره مرجع')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='تاریخ آپدیت')),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.address', verbose_name='آدرس')),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.coupon', verbose_name='کد تخفیف')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_payment', to='orders.payment', verbose_name='فاکتور')),
            ],
            options={
                'verbose_name': 'سفارش',
                'verbose_name_plural': 'سفارشات',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='نام خریدار')),
                ('products', models.TextField(verbose_name='محصولات سفارش داده شده')),
                ('total_price', models.PositiveIntegerField(verbose_name='مبلغ کل')),
                ('payment_status', models.CharField(choices=[('در انتظار پرداخت', 'در انتظار پرداخت'), ('پرداخت موفق', 'پرداخت موفق'), ('پرداخت ناموفق', 'پرداخت ناموفق'), ('پرداخت درب منزل', 'پرداخت درب منزل')], default='در انتظار پرداخت', max_length=30, verbose_name='وضعیت پرداخت')),
                ('address', models.TextField(verbose_name='آدرس تحویل')),
                ('created', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='خریدار')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='orders.order', verbose_name='سفارش')),
            ],
            options={
                'verbose_name': 'فاکتور',
                'verbose_name_plural': 'فاکتورها',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(default='', max_length=255, verbose_name='نام محصول')),
                ('product_code', models.CharField(default='', max_length=50, verbose_name='کد محصول')),
                ('product_unit_price', models.PositiveIntegerField(default=0, verbose_name='قیمت واحد محصول')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='تعداد')),
                ('price', models.PositiveIntegerField(help_text='به تومان', verbose_name='جمع قیمت (محاسبه شده با تعداد)')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='تاریخ آپدیت')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='orders.order', verbose_name='سفارش')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.product', verbose_name='محصول')),
            ],
            options={
                'verbose_name': 'آیتم سفارش',
                'verbose_name_plural': 'آیتم\u200cهای سفارش',
            },
        ),
    ]
