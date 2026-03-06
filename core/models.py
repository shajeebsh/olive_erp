from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    is_employee = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to="profile_images/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
