from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    is_employee = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to="profile_images/", null=True, blank=True)
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def has_role(self, role_name, company):
        return self.user_roles.filter(role__name=role_name, company=company).exists()

    def get_company_permissions(self, company):
        roles = self.user_roles.filter(company=company)
        perms = set()
        for ur in roles:
            for perm in ur.role.permissions.all():
                perms.add(f"{perm.content_type.app_label}.{perm.codename}")
        return perms

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50)
    object_repr = models.CharField(max_length=255)
    changes = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("audit log")
        verbose_name_plural = _("audit logs")

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action} {self.model_name}"


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField('auth.Permission', blank=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'role', 'company')
        verbose_name = _("user role")
        verbose_name_plural = _("user roles")

    def __str__(self):
        return f"{self.user} - {self.role} @ {self.company}"
