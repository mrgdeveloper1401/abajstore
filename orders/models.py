from django.db import models
from django.utils import timezone
from products.models import Product
import django_jalali.db.models as jmodels
from django.utils.translation import gettext as _
from accounts.models import User, Address
import jdatetime
import pytz


class Coupon(models.Model):
    code = models.CharField(_('کد'), max_length=30, unique=True)
    value = models.PositiveSmallIntegerField(_('مقدار'), help_text=_('مقدار تخفیف به درصد'))
    # valid_from = models.DateField()
    valid_until = models.DateField(_('معتبر تا تاریخ'), )
    active = models.BooleanField(_('فعال'), default=True)

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کد تخفیف"

    def __str__(self):
        return self.code


class Order(models.Model):
    ORDER_STATUS = [
        ("1", _("در انتظار پرداخت")),
        ("2", _("پرداخت درب منزل")),
        ("3", _("پرداخت شده")),
        ("4", _("ارسال شده")),
        ("5", _("تحویل داده شده")),
        ("6", _("لغو شده")),
    ]
    TIME_SLOTS = [
        (1, _('08:00 - 10:00')),
        (2, _('10:00 - 12:00')),
        (3, _('12:00 - 14:00')),
        (4, _('14:00 - 16:00')),
        (5, _('16:00 - 18:00')),
        (6, _('18:00 - 20:00')),
        (7, _('20:00 - 22:00')),
        (8, _('22:00 - 24:00')),
    ]
    DELIVERY_TYPES = [
        ("ارسال زماندار", _("ارسال زماندار")),
        ("ارسال فوری", _("ارسال فوری")),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    code = models.CharField(_('کد سفارش'), max_length=15, unique=True, db_index=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='آدرس')
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='فاکتور',
                                related_name='order_payment')
    time_slot = models.IntegerField(_('بازه زمانی'), choices=TIME_SLOTS, db_index=True)
    delivery_date = models.DateField(_('تاریخ ارسال'), default=timezone.now)
    delivery_type = models.CharField(_('نوع ارسال'), choices=DELIVERY_TYPES, max_length=20, default='ارسال زماندار')
    send_price = models.PositiveIntegerField(_('هزینه ی ارسال'), default=0, help_text='به تومان')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL,null=True, blank=True, verbose_name='کد تخفیف')
    status = models.CharField(_('وضعیت'), max_length=20, choices=ORDER_STATUS, default='در انتظار پرداخت')
    rrn = models.CharField(_('شماره مرجع'), max_length=50, null=True, blank=True,
                           help_text='شماره یکتایی که بانک بعد از اتمام موفق تراکنش،'
                                     ' همراه با شماره درخواست به پذیرنده میدهد.'
                                     ' این شماره جهت پیگیریهای مالی استفاده میگردد.')

    created = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated = models.DateTimeField(_('تاریخ آپدیت'), auto_now=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"

    def __str__(self):
        return str(self.code)

    def get_price(self):
        if self.order_items:
            total_price = sum(item.price for item in self.order_items.all())

            if self.coupon:
                return total_price - (total_price * (self.coupon.value / 100))

            return total_price
        return 0

    def get_price_with_send(self):
        return int(self.get_price() + self.send_price)

    def created_to_jalali(self):
        return jdatetime.date.fromgregorian(date=self.created)

    def created_datetime_to_jalali(self):
        tehran_timezone = pytz.timezone('Asia/Tehran')
        dt_tehran = timezone.localtime(self.created, tehran_timezone)
        return jdatetime.datetime.fromgregorian(datetime=dt_tehran)

    def get_status_color(self):
        status_colors = {
            'در انتظار پرداخت': 'warning',
            'پرداخت درب منزل': 'info',
            'پرداخت شده': 'success',
            'ارسال شده': 'primary',
            'تحویل داده شده': 'dark',
            'لغو شده': 'danger'
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_delivery_type_badge(self):
        return 'فوری' if self.delivery_type == 'ارسال فوری' else 'زماندار'

 
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name='سفارش')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='محصول')
    product_name = models.CharField(_('نام محصول'), max_length=255, default='')  
    product_code = models.CharField(_('کد محصول'), max_length=50, default='')  
    product_unit_price = models.PositiveIntegerField(_('قیمت واحد محصول'), default=0)  # 👈 اضافه شد
    quantity = models.PositiveIntegerField(_('تعداد'), default=1)
    price = models.PositiveIntegerField(_('جمع قیمت (محاسبه شده با تعداد)'), help_text='به تومان')

    created = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated = models.DateTimeField(_('تاریخ آپدیت'), auto_now=True)

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.order} - {self.product.name}"


class Payment(models.Model):
    PAYMENT_STATUS = [
        ("در انتظار پرداخت", _("در انتظار پرداخت")),
        ("پرداخت موفق", _("پرداخت موفق")),
        ("پرداخت ناموفق", _("پرداخت ناموفق")),
    ]
    BANK = [
        ("پارسیان", _("پارسیان")),
        ("ملت", _("ملت")),
    ]
    bank = models.CharField(_('درگاه'), max_length=10, choices=BANK, null=True, blank=True)
    token = models.CharField(_('شناسه پرداخت'), max_length=255)
    rrn = models.CharField(_('شماره مرجع'), max_length=50, null=True, blank=True)
    terminal_no = models.CharField(_('شماره ترمینال'), max_length=50, null=True, blank=True)
    amount = models.CharField(_('مبلغ'), max_length=20, default=0)
    hash_card_no = models.CharField(_('شماره کارت (هش شده)'), max_length=100, default=0)
    response_code = models.CharField(_('کد پاسخ سرور'), max_length=100, default=0)
    response = models.JSONField(_('پاسخ سرور'), default=dict)
    status = models.CharField(_('وضعیت'),max_length=30, choices=PAYMENT_STATUS, default='در انتظار پرداخت')

    created = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated = models.DateTimeField(_('تاریخ آپدیت'), auto_now=True)
    def __str__(self):
        return self.token

    def created_datetime_to_jalali(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created)


class Invoice(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, verbose_name=_('سفارش'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('خریدار'))
    buyer_name = models.CharField("نام خریدار", max_length=255, blank=True, null=True)
    products = models.TextField(_('محصولات سفارش داده شده'))  # لیست محصولات به عنوان متن ذخیره می‌شود
    total_price = models.PositiveIntegerField(_('مبلغ کل'))
    payment_status = models.CharField(_('وضعیت پرداخت'), max_length=30, choices=[
        ('در انتظار پرداخت', 'در انتظار پرداخت'),
        ('پرداخت موفق', 'پرداخت موفق'),
        ('پرداخت ناموفق', 'پرداخت ناموفق'),
        ('پرداخت درب منزل', 'پرداخت درب منزل'),
    ], default='در انتظار پرداخت')
    address = models.TextField(_('آدرس تحویل'))
    created = jmodels.jDateTimeField(_('تاریخ ایجاد'), auto_now_add=True)

    class Meta:
        verbose_name = "فاکتور"
        verbose_name_plural = "فاکتورها"

    def __str__(self):
        return f"فاکتور سفارش {self.order.code}"

    def created_to_jalali(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created)
