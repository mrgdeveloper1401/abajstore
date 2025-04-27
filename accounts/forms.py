from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, OTP, Address
from utils.validators import *


class UserCreationForm(forms.ModelForm):
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 outline-none focus:border-submitPageColorBorderBlue transition-all',
                                      'placeholder': 'شماره موبایل'}),
        error_messages={
            'required': 'لطفا شماره موبایل خود را وارد کنید.',
            'invalid': 'شماره تلفن نامعتبر است.',
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 outline-none focus:border-submitPageColorBorderBlue transition-all',
                                          'placeholder': 'رمز عبور'}),
        error_messages={
            'required': 'لطفا گذرواژه خود را وارد کنید.',
            'invalid': 'گذرواژه وارد شده صحیح نیست.',
        }
    )

    class Meta:
        model = User
        fields = ('phone_number', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 outline-none focus:border-submitPageColorBorderBlue transition-all',
                                      'placeholder': 'شماره موبایل'}),
        error_messages={
            'required': 'لطفا شماره موبایل خود را وارد کنید.',
            'invalid': 'کاربری با این شماره یافت نشد.',
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 outline-none focus:border-submitPageColorBorderBlue transition-all',
                                          'placeholder': 'رمز عبور'}),
        error_messages={
            'required': 'لطفا گذرواژه خود را وارد کنید.',
            'invalid': 'گذرواژه وارد شده صحیح نیست.',
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = 'شماره موبایل یا رمز اشتباه است!'
        self.fields['username'].error_messages = {'required': 'شماره موبایل را وارد کنید'}
        self.fields['password'].error_messages = {'required': 'رمز عبور را وارد کنید'}

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(phone_number=username).exists():
            raise forms.ValidationError("این شماره موبایل در سیستم ثبت ‌نام نشده است.")
        return username


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text=
                                         "برای تغییر گذرواژه  <a href=\"../password/\"> وارد شوید </a>.")

    class Meta:
        model = User
        fields = '__all__'


class ForgetPasswordForm(forms.Form):
    phone_number = forms.CharField(max_length=11, validators=[persian_phone_number_validation, ], label='شماره موبایل',
                                   widget=forms.TextInput(attrs={
                                       'class': 'border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 '
                                                'outline-none focus:border-submitPageColorBorderBlue transition-all',
                                       'placeholder': '09123456789'
                                   }))

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        try:
            User.objects.get(phone_number__exact=phone_number)
        except User.DoesNotExist:
            raise forms.ValidationError('کاربری با این شماره یافت نشد!')

        return phone_number


class OTPForm(forms.Form):
    code = forms.CharField(max_length=10,
                           widget=forms.TextInput(attrs={
                                   'class': 'border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2'
                                            ' outline-none focus:border-submitPageColorBorderBlue transition-all',
                                   'placeholder': 'کد تایید را وارد کنید...'
                               }))

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit():
            raise forms.ValidationError('کد را فقط به صورت عددی و به لاتین وارد کنید')

        try:
            OTP.objects.get(code=code)
        except OTP.DoesNotExist:
            raise forms.ValidationError('کد وارد شده اشتباه است!')

        return code


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='رمز عبور فعلی',
        widget=forms.TextInput(attrs={
            'class': 'outline-none px-2 py-3 rounded border-2 border-submitPageColorBorderLowBlack '
                     'focus:border-2 focus:border-submitPageColorBorderBlue',
            'placeholder': 'رمز عبور فعلی'
        }),
        required=True
    )
    new_password = forms.CharField(
        label='رمز عبور جدید',
        widget=forms.TextInput(attrs={
            'class': 'outline-none px-2 py-3 rounded border-2 border-submitPageColorBorderLowBlack '
                     'focus:border-2 focus:border-submitPageColorBorderBlue',
            'placeholder': 'رمز عبور جدید'
        }),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        if not self.user.check_password(self.cleaned_data['current_password']):
            raise ValidationError("رمز عبور فعلی نادرست است.")
        return self.cleaned_data['current_password']

    def save(self):
        new_password = self.cleaned_data['new_password']
        self.user.set_password(new_password)
        self.user.save()
        return self.user


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'outline-none px-2 py-3 rounded border-2 border-submitPageColorBorderLowBlack'
                            ' focus:border-2 focus:border-submitPageColorBorderBlue',
                   'placeholder': 'نام'}), required=False
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'outline-none px-2 py-3 rounded border-2 border-submitPageColorBorderLowBlack '
                            'focus:border-2 focus:border-submitPageColorBorderBlue',
                   'placeholder': 'نام خانوادگی'}), required=False
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'outline-none px-2 py-3 rounded border-2 border-submitPageColorBorderLowBlack '
                            'focus:border-2 focus:border-submitPageColorBorderBlue',
                   'placeholder': 'شماره موبایل'}),
    )
    card_number = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'outline-none px-2 py-3 rounded border-2 border-submitPageColorBorderLowBlack '
                            'focus:border-2 focus:border-submitPageColorBorderBlue',
                   'placeholder': 'شماره کارت'}), required=False
    )
    shaba_number = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'outline-none px-2 py-3 rounded border-2 border-submitPageColorBorderLowBlack '
                            'focus:border-2 focus:border-submitPageColorBorderBlue',
                   'placeholder': 'شماره شبا'}), required=False
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'card_number', 'shaba_number')

    def clean_phone_number(self):
        value = self.cleaned_data.get('phone_number')
        user = User.objects.filter(phone_number=value).exclude(id=self.instance.id)
        if user.exists():
            raise ValidationError('کاربری با این شماره از قبل وجود دارد!')
        return value


class AddressForm(forms.ModelForm):
    location = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'offsetsMap'}), required=False)

    receiver_name = forms.CharField(
        validators=[persian_characters, ],
        widget=forms.TextInput(
            attrs={'class': 'onlyPersianLetters border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 outline-none focus:border-submitPageColorBorderBlue transition-all',
                   'placeholder': 'نام گیرنده',
                   'id': 'receiver_name'})
    )
    phone_number = forms.CharField(
        validators=[persian_phone_number_validation],
        widget=forms.NumberInput(
            attrs={'class': 'border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 outline-none'
                            ' focus:border-submitPageColorBorderBlue transition-all',
                   'placeholder': 'شماره تماس گیرنده',
                   'id': 'phone_number'})
    )
    city = forms.CharField(
        widget=forms.Select(
            attrs={'class': 'border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 outline-none'
                            ' focus:border-submitPageColorBorderBlue transition-all',
                   'id': 'city'}),
        required=False
    )
    address = forms.CharField(
        validators=[persian_address],
        widget=forms.TextInput(
            attrs={'class': 'onlyPersianLetters border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 outline-none '
                            'focus:border-submitPageColorBorderBlue transition-all',
                   'placeholder': 'آدرس',
                   'id': 'address'})
    )
    # location = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={'class': 'onlyPersianLetters border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 outline-none '
    #                         'focus:border-submitPageColorBorderBlue transition-all',
    #                'placeholder': 'لوکیشن',
    #                'id': 'location'})
    # )
    postalcode = forms.CharField(
        validators=[only_number],
        widget=forms.NumberInput(
            attrs={'class': 'border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 outline-none'
                            ' focus:border-submitPageColorBorderBlue transition-all',
                   'placeholder': 'کدپستی'}), required=False
    )
    note = forms.CharField(
        validators=[],
        widget=forms.TextInput(
            attrs={'class': 'border-submitPageColorBorderLowBlack border-2 w-full py-2 px-2 outline-none'
                            ' focus:border-submitPageColorBorderBlue transition-all',
                   'placeholder': 'یادداشت..'}), required=False
    )

    class Meta:
        model = Address
        fields = ['receiver_name', 'phone_number', 'city', 'address', 'location', 'postalcode', 'note']

        def __init__(self, *args, **kwargs):
            self.user = kwargs.pop('user', None)
            super().__init__(*args, **kwargs)

        def save(self, commit=True):
            instance = super().save(commit=False)
            if self.user:
                instance.user = self.user
            if commit:
                instance.save()
            return instance

    # def clean_location(self):
    #     location_data = self.cleaned_data['offsets']
    #
    #     # if isinstance(location_data, list):
    #     #     return location_data
    #     return location_data
    #
    #     # raise forms.ValidationError("داده‌ی ورودی باید یک لیست باشد.")
