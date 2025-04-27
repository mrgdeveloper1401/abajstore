from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import User, OTP, Address
from accounts.forms import UserCreationForm, UserChangeForm


admin.site.site_header = 'پنل مدیریت آباج استور'
admin.site.index_title = ''
admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    list_display_links = ("id", "phone_number")
    list_display = ("id", "phone_number", "full_name", "is_superuser", "created")
    list_filter = ("is_superuser", )
    searching_fields = ("phone_number", "first_name", "last_name")
    ordering = ("-created", )
    fieldsets = (
        (
            None,
            {
                "fields": ("phone_number",
                           "first_name",
                           "last_name",
                           "card_number",
                           "shaba_number",
                           "password",
                           "last_login"),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "first_name",
                    "last_name",
                    "password",
                    "is_superuser",
                ),
            },
        ),
    )

    def full_name(self, obj):
        return obj.get_full_name
    full_name.short_description = 'نام و نام خانوادگی'


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "code", "created")
    list_filter = ("created", )
    search_fields = ("phone_number",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "get_user", "receiver_name", "phone_number", "state", "city")
    list_filter = ("state", "city")
    search_fields = ("phone_number", "city")
    autocomplete_fields = ("user", )
    list_display_links = ("id", "get_user")
    raw_id_fields = ("user",)

    def get_user(self, obj):
        return obj.user
    get_user.short_description = 'کاربر'
