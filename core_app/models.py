from django.db import models


class CreateMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UpdateMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    deleted_at = models.DateTimeField(editable=False, blank=True, null=True)
    is_deleted = models.BooleanField(default=None, editable=False, null=True, blank=True)

    class Meta:
        abstract = True


# class OwnerMixin(models.Model):
#     created_by = models.ForeignKey(
#         "accounts.UserModel",
#         on_delete=models.PROTECT,
#         verbose_name="ایجاد کننده",
#         related_name="%(class)s_created",
#         null=True,
#         editable=False,
#     )
#
#     class Meta:
#         abstract = True
