from django.core.exceptions import ValidationError
import re


def persian_phone_number_validation(value):
    pattern = r'^09\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError('شماره تلفن معتبر وارد کنید!(مثال : 09123456789)')
    return True


def persian_national_code(value):
    pattern = r'^[0-9]{10}$'
    if not re.match(pattern, value):
        raise ValidationError('کدملی نامعتبر است!')
    return True


def persian_characters(value):
    pattern = r'^[\u0600-\u06FF\s]+$'
    if not re.match(pattern, value):
        raise ValidationError('فقط حروف فارسی معتبر است!')
    return True


def persian_address(value):
    pattern = r'^[\u0600-\u06FF\s\d-]+$'
    if not re.match(pattern, value):
        raise ValidationError('فقط حروف فارسی معتبر است!')
    return True


def persian_postalcode(value):
    # pattern = r'\b(?!(\d)\1{3})[13-9]{4}[1346-9][013-9]{5}\b'
    # if not re.match(pattern, value):
    #     raise ValidationError('کدپستی نامعتبر است!')
    return True


def persian_phone(value):
    pattern = r'^0[0-9]{2,}-[0-9]{7,}$'
    if not re.match(pattern, value):
        raise ValidationError('تلفن ثابت با پیش شماره وارد کنید(1234567-021)!')
    return True


def only_number(value):
    pattern = r'^[0-9]*$'
    if not re.match(pattern, value):
        raise ValidationError('فقط اعداد مجاز است')
    return True


def persian_date(value):
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('تاریخ را به صورت 01-01-1400 وارد کنید')
    return True
