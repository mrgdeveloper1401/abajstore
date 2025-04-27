import logging

from django import forms
from .models import Order, Coupon
from accounts.models import Address
import datetime
import jdatetime
import pytz


class CouponForm(forms.Form):
    coupon_code = forms.CharField(max_length=50)

    def clean_coupon_code(self):
        code = self.cleaned_data['coupon_code']
        try:
            coupon = Coupon.objects.get(code=code, active=True)
            if not coupon.is_valid():
                raise forms.ValidationError('کد تخفیف منقضی شده است!')
            return coupon
        except Coupon.DoesNotExist:
            raise forms.ValidationError('کد تخفیف نامعتبر است!')


class OrderForm(forms.ModelForm):
    address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        required=True,
        label='آدرس',
        empty_label='-------------'
    )
    pay_method = forms.CharField(
        required=True,
        widget=forms.RadioSelect(
            attrs={'class': 'payMethodCheckBox', },
            choices=(("پرداخت درب منزل", "پرداخت درب منزل"),
                     ("درگاه پارسیان", "درگاه پارسیان"),
                     ("درگاه بانک ملت", "درگاه بانک ملت")
                     ),
        )
    )
    delivery_date = forms.CharField(max_length=11, required=False)
    # delivery_date = forms.CharField(
    #     required=True,
    #     widget=forms.TextInput(
    #         attrs={'class': '',
    #                }
    #     ),
    # )
    delivery_type = forms.CharField(max_length=20, required=False)
    # delivery_type = forms.CharField(
    #     required=True,
    #     label='نوع ارسال',
    #     widget=forms.RadioSelect(
    #         attrs={'class': '',
    #                },
    #         choices=(("ارسال زماندار", "ارسال زماندار"),
    #                  ("ارسال فوری", "ارسال فوری"),
    #                  ),
    #     ),
    # )
    time_slot = forms.IntegerField(required=False)

    class Meta:
        model = Order
        fields = ['address', 'pay_method', 'delivery_date', 'time_slot', 'delivery_type']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['address'].queryset = Address.objects.filter(user=user, active=True)

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise forms.ValidationError('آدرس انتخاب نشده است!')
        return address

    def clean_pay_method(self):
        pay_method = self.cleaned_data.get('pay_method')
        if pay_method not in ['پرداخت درب منزل', 'درگاه پارسیان', 'درگاه بانک ملت']:
            raise forms.ValidationError('روش پرداخت صحیح وارد کنید!')
        return pay_method

    # def __init__(self, *args, **kwargs):
    #     user = kwargs.pop('user', None)
    #     super().__init__(*args, **kwargs)
    #     if user:
    #         self.fields['address'].queryset = Address.objects.filter(user=user)
    #         self.fields['address'].widget.attrs.update({
    #             'class': 'form-control',
    #             'placeholder': 'انتخاب آدرس'
    #         })

    def clean_delivery_date(self):
        jalali_date_str = self.cleaned_data['delivery_date']

        if jalali_date_str:
            try:
                year, month, day = map(int, jalali_date_str.split('-'))
                jalali_date = jdatetime.date(year, month, day)
                gregorian_date = jalali_date.togregorian()
            except ValueError:
                raise forms.ValidationError('فرمت تاریخ نامعتبر است.')

            if gregorian_date < datetime.date.today():
                raise forms.ValidationError('تاریخ ارسال نمی‌تواند در گذشته باشد.')

        else:
            gregorian_date = datetime.date.today()

        return gregorian_date

    def clean(self):
        cleaned_data = super().clean()
        pay_method = cleaned_data.get('pay_method')
        delivery_type = cleaned_data.get('delivery_type')
        delivery_date = cleaned_data.get('delivery_date')
        time_slot = cleaned_data.get('time_slot')
        now = datetime.datetime.now(pytz.timezone('Asia/Tehran'))
        today = datetime.date.today()

        if not pay_method:
            raise forms.ValidationError('لطفا یک روش پرداخت انتخاب کنید!')

        if delivery_date < today:
            raise forms.ValidationError('این بازه زمانی در گذشته است و نمی‌توان آن را انتخاب کرد.')

        if time_slot and delivery_date == datetime.date.today():
            current_hour = now.hour
            current_time_slot = 0

            if current_hour >= 22:
                current_time_slot = 8
            elif current_hour >= 20:
                current_time_slot = 7
            elif current_hour >= 18:
                current_time_slot = 6
            elif current_hour >= 16:
                current_time_slot = 5
            elif current_hour >= 14:
                current_time_slot = 4
            elif current_hour >= 12:
                current_time_slot = 3
            elif current_hour >= 10:
                current_time_slot = 2
            elif current_hour >= 8:
                current_time_slot = 1

            if time_slot < current_time_slot:
                raise forms.ValidationError('این بازه زمانی گذشته است و نمی‌توان آن را انتخاب کرد!')

        if delivery_type == 'ارسال زماندار' and delivery_date and time_slot:
            max_order = Order.objects.filter(time_slot=time_slot,
                                             delivery_date=datetime.date.today())

            if max_order.count() >= 10:
                raise forms.ValidationError('از حداکثر میزان سفارش در این بازه زمانی استفاده شده است.'
                                            ' لطفا از بازه زمانی دیگری استفاده کنید.')

        if delivery_type == 'ارسال زماندار' and (not delivery_date or not time_slot):
            raise forms.ValidationError('لطفا یک بازه زمانی انتتخاب کنید.')

        return cleaned_data
