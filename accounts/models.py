from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from utils.validators import *


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_('نام'), max_length=50, null=True, blank=True, validators=[persian_characters, ])
    last_name = models.CharField(_('نام خوانوادگی'), max_length=50, null=True, blank=True, validators=[persian_characters, ])
    phone_number = models.CharField(_('شماره موبایل'), max_length=11, unique=True,
                                    validators=[persian_phone_number_validation, ])

    card_number = models.CharField(_('شماره کارت'), max_length=16, null=True, blank=True)
    shaba_number = models.CharField(_('شماره شبا'), max_length=30, null=True, blank=True)

    is_staff = models.BooleanField(_('ادمین'), default=False)
    is_superuser = models.BooleanField(_('ادمین اصلی'), default=False)
    is_verified = models.BooleanField(_('تایید شده'), default=False)

    created = models.DateField(_("تاریخ ثبتنام"), auto_now_add=True)
    updated = models.DateField(_("تاریخ آپدیت"), auto_now=True)

    USERNAME_FIELD = 'phone_number'

    objects = UserManager()

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return f'User ID: {self.id} - {self.phone_number}'

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


class OTP(models.Model):
    """
    One Time Password is for register and forget password.
    """
    phone_number = models.CharField(_('شماره موبایل'), max_length=11,
                                    validators=[persian_phone_number_validation, ])
    code = models.PositiveIntegerField(_('کد یکبارمصرف'))
    created = models.DateField(_('تاریخ تولید'), auto_now_add=True)

    class Meta:
        verbose_name = _('کد یکبارمصرف')
        verbose_name_plural = _('کد یکبارمصرف')

    def __str__(self):
        return f"{self.phone_number} - {self.code}"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address')
    receiver_name = models.CharField(_('نام گیرنده'), max_length=50, validators=[persian_characters, ])
    phone_number = models.CharField(_('شماره موبایل گیرنده'), max_length=11,
                                    validators=[persian_phone_number_validation, ])
    state = models.CharField(_('استان'), default='یزد', max_length=30)
    city = models.CharField(_('شهر'), max_length=30, default='یزد')
    postalcode = models.CharField(_('کد پستی'), null=True, blank=True, max_length=20, validators=[only_number, ])
    address = models.TextField(_('آدرس'))
    location = models.JSONField(null=True, blank=True)
    note = models.TextField(_('یادداشت'), blank=True, null=True)
    active = models.BooleanField(_('فعال'), default=True)
    created = models.DateField(_('تاریخ ایجاد'), auto_now_add=True)

    class Meta:
        verbose_name = _('آدرس ها')
        verbose_name_plural = _('آدرس ها')
        ordering = ('-created', )

    def __str__(self):
        return f'{self.city} - {self.address[:25]}..'

    def receiver_info(self):
        return f'{self.receiver_name}\n {self.phone_number}'

    def get_full_address(self):
        return f'{self.city} - {self.address} - {self.postalcode if self.postalcode is not None else ""}'
