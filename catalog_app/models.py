from django.db import models
from django.utils.text import slugify
import os

from core_app.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from .validations import validate_image_size


def image_upload_path(instance, filename):
    """Generate upload path based on model name and image title."""
    base_filename, file_extension = os.path.splitext(filename)
    return f"catalog/images/{slugify(instance.title)}/{slugify(base_filename)}{file_extension}"


class Image(CreateMixin, UpdateMixin, SoftDeleteMixin):
    # user = models.ForeignKey("accounts.UserModel", on_delete=models.PROTECT, related_name="user_upload_user",
    #                          null=True)
    # فیلدهای اصلی
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان تصویر",
        help_text="عنوان توصیفی برای تصویر (ضروری)"
    )
    image_file = models.ImageField(
        upload_to=image_upload_path,
        verbose_name="فایل تصویر",
        help_text="فرمت‌های پشتیبانی: JPG, PNG, WebP",
        width_field="image_width",
        height_field="image_height",
        validators=[validate_image_size]
    )
    image_width = models.PositiveIntegerField(editable=False, null=True)
    image_height = models.PositiveIntegerField(editable=False, null=True)
    image_url = models.CharField(max_length=255, editable=False, null=True)
    caption = models.TextField(
        blank=True,
        verbose_name="توضیح تصویر",
        help_text="توضیح اختیاری درباره تصویر"
    )

    # مدیریت فایل
    file_size = models.PositiveIntegerField(
        editable=False,
        null=True,
        verbose_name="حجم فایل (بایت)"
    )
    file_format = models.CharField(
        max_length=10,
        editable=False,
        verbose_name="فرمت فایل"
    )

    class Meta:
        verbose_name = "تصویر"
        verbose_name_plural = "تصاویر"
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """محاسبه خودکار فرمت، حجم فایل و ابعاد تصویر قبل از ذخیره."""
        if self.image_file:
            self.file_size = self.image_file.size
            self.file_format = os.path.splitext(self.image_file.name)[1][1:].upper()
            self.image_url = self.image_file.url
        super().save(*args, **kwargs)
