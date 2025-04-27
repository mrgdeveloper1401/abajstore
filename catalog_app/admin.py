from django.contrib import admin
from django.utils.html import format_html
from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    # تنظیمات نمایش لیست تصاویر
    list_display = ('title', "id", 'file_format', 'file_size_mb', 'created_at')
    list_filter = ('file_format', 'created_at')
    search_fields = ('title', )
    search_help_text = "برای جست و جو میتوانید از عنوان عکس استفاده کنید"
    readonly_fields = ('thumbnail_preview', 'file_format', 'file_size', 'image_width', 'image_height', 'created_at',
                       'updated_at', "image_url")
    # list_editable = ('is_active',)  # امکان تغییر وضعیت فعال/غیرفعال مستقیم از لیست
    ordering = ('-created_at',)
    list_per_page = 20

    # فیلدهای گروه‌بندی شده در صفحه ویرایش
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'image_file', 'thumbnail_preview', 'caption', "image_url")
        }),
        ('مشخصات فایل', {
            'fields': ('file_format', 'file_size', 'image_width', 'image_height'),
            'classes': ('collapse',)  # قابل جمع‌شدن
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # نمایش پیش‌نمایش تصویر در لیست و صفحه ویرایش
    def thumbnail_preview(self, obj):
        if obj.image_file:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; object-fit: cover;" />',
                obj.image_file.url
            )
        return "-"
    thumbnail_preview.short_description = "پیش‌نمایش"

    # نمایش حجم فایل به صورت مگابایت (خوانا‌تر)
    def file_size_mb(self, obj):
        if obj.file_size:
            return f"{obj.file_size / (1024 * 1024):.2f} MB"
        return "-"
    file_size_mb.short_description = "حجم فایل (MB)"
