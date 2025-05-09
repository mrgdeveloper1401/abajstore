# Generated by Django 5.1.8 on 2025-04-26 05:49

import django.db.models.deletion
import utils.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=11, validators=[utils.validators.persian_phone_number_validation], verbose_name='شماره موبایل')),
                ('code', models.PositiveIntegerField(verbose_name='کد یکبارمصرف')),
                ('created', models.DateField(auto_now_add=True, verbose_name='تاریخ تولید')),
            ],
            options={
                'verbose_name': 'کد یکبارمصرف',
                'verbose_name_plural': 'کد یکبارمصرف',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True, validators=[utils.validators.persian_characters], verbose_name='نام')),
                ('last_name', models.CharField(blank=True, max_length=50, null=True, validators=[utils.validators.persian_characters], verbose_name='نام خوانوادگی')),
                ('phone_number', models.CharField(max_length=11, unique=True, validators=[utils.validators.persian_phone_number_validation], verbose_name='شماره موبایل')),
                ('card_number', models.CharField(blank=True, max_length=16, null=True, verbose_name='شماره کارت')),
                ('shaba_number', models.CharField(blank=True, max_length=30, null=True, verbose_name='شماره شبا')),
                ('is_staff', models.BooleanField(default=False, verbose_name='ادمین')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='ادمین اصلی')),
                ('is_verified', models.BooleanField(default=False, verbose_name='تایید شده')),
                ('created', models.DateField(auto_now_add=True, verbose_name='تاریخ ثبتنام')),
                ('updated', models.DateField(auto_now=True, verbose_name='تاریخ آپدیت')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'کاربر',
                'verbose_name_plural': 'کاربران',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver_name', models.CharField(max_length=50, validators=[utils.validators.persian_characters], verbose_name='نام گیرنده')),
                ('phone_number', models.CharField(max_length=11, validators=[utils.validators.persian_phone_number_validation], verbose_name='شماره موبایل گیرنده')),
                ('state', models.CharField(default='یزد', max_length=30, verbose_name='استان')),
                ('city', models.CharField(default='یزد', max_length=30, verbose_name='شهر')),
                ('postalcode', models.CharField(blank=True, max_length=20, null=True, validators=[utils.validators.only_number], verbose_name='کد پستی')),
                ('address', models.TextField(verbose_name='آدرس')),
                ('location', models.JSONField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True, verbose_name='یادداشت')),
                ('active', models.BooleanField(default=True, verbose_name='فعال')),
                ('created', models.DateField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='address', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'آدرس ها',
                'verbose_name_plural': 'آدرس ها',
                'ordering': ('-created',),
            },
        ),
    ]
