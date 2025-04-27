from django.contrib.auth.models import BaseUserManager
from utils.validators import persian_phone_number_validation


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, phone_number, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """

        if not phone_number:
            raise ValueError("شماره تلفن خود را وارد کنید..")
        if not persian_phone_number_validation(phone_number):
            raise ValueError("شماره تلفن خود را به صورت : 09123456789 وارد کنید")

        user = self.model(phone_number=phone_number)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        user = self.create_user(phone_number, password, **extra_fields)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
