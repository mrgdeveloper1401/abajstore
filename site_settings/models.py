from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext as _
from utils.validators import persian_phone_number_validation


class SingletonModel(models.Model):
    """Base class for singleton models"""
    class Meta:
        abstract = True

    @classmethod
    def get_solo(cls):
        return cls.objects.get_or_create(pk=1)[0]


class BannerImages(models.Model):
    setting = models.ForeignKey('SiteSettings', on_delete=models.CASCADE, related_name='banner_images', default=1)
    banner = models.ImageField(_('بنر'), upload_to='banners/', help_text='عکس برای بنر')
    # link = models.CharField(_('لینک'), max_length=250, null=True, blank=True)

    def __str__(self):
        return str(self.banner.name)


class SiteSettings(SingletonModel):
    header_message = models.TextField(_('اعلانات'), blank=True, null=True)
    admin_phone_number = models.CharField(_('شماره موبایل ادمین'), max_length=11,
                                          validators=[persian_phone_number_validation, ],
                                          help_text='برای ارسال پیام های اطلاع رسانی و سفارش جدید.')
    fast_send_price = models.PositiveIntegerField(_('هزینه ی ارسال فوری'), default=0, help_text='به تومان')

    pay_with_mellat = models.BooleanField(_('درگاه ملت'), default=True)
    pay_with_parsian = models.BooleanField(_('درگاه پارسیان'), default=True)
    pay_at_home = models.BooleanField(_('پرداخت درب منزل'), default=True)

    # special_offer_percent = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)],
    #                                                          default=10,
    #                                                          help_text='محصولاتی که بیشتر از این درصد تخفیف '
    #                                                                    'داشته باشند در بخش تخفیف ویژه قرار میگیرند.')

    class Meta:
        verbose_name = _('تنظیمات')
        verbose_name_plural = _('تنظیمات')

    def __str__(self):
        return 'تنظیمات صفحه اصلی'


class Base(models.Model):
    name = models.CharField(_('نام'), max_length=100)
    value = models.CharField(_('مقدار'), max_length=250)

    def __str__(self):
        return self.name


class Link(Base):
    setting = models.ForeignKey(SiteSettings, on_delete=models.CASCADE, default=1, related_name='links')


class Address(Base):
    setting = models.ForeignKey(SiteSettings, on_delete=models.CASCADE, default=1, related_name='address')


class Phone(Base):
    setting = models.ForeignKey(SiteSettings, on_delete=models.CASCADE, default=1, related_name='phone')
