from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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


class ApprovalWorkflow(models.Model):
    """
    Reusable approval workflow for high-risk ERP operations.
    Supports journal posting, dividend approvals, purchasing thresholds, etc.
    """
    STATUS_CHOICES = [
        ('PE', 'Pending'),
        ('AP', 'Approved'),
        ('RJ', 'Rejected'),
    ]
    
    WORKFLOW_TYPES = [
        ('JOURNAL_POST', 'Journal Posting'),
        ('DIVIDEND', 'Dividend Approval'),
        ('PURCHASE_ORDER', 'Purchase Order Approval'),
        ('TAX_FILING', 'Tax Filing Approval'),
    ]
    
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    workflow_type = models.CharField(max_length=20, choices=WORKFLOW_TYPES)
    reference_id = models.CharField(max_length=100, help_text="ID of the object being approved")
    reference_model = models.CharField(max_length=50, help_text="Model name, e.g. JournalEntry, Dividend")
    
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='PE')
    
    requested_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='approval_requests'
    )
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approvals_given'
    )
    
    request_notes = models.TextField(blank=True)
    approval_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "approval workflow"
        verbose_name_plural = "approval workflows"
    
    def __str__(self):
        return f"{self.get_workflow_type_display()} - {self.reference_id} ({self.get_status_display()})"
    
    def approve(self, user, notes=''):
        self.status = 'AP'
        self.approved_by = user
        self.approval_notes = notes
        from django.utils import timezone
        self.decided_at = timezone.now()
        self.save()
    
    def reject(self, user, notes=''):
        self.status = 'RJ'
        self.approved_by = user
        self.approval_notes = notes
        from django.utils import timezone
        self.decided_at = timezone.now()
        self.save()


class DocumentAttachment(models.Model):
    """
    Generic document attachment for ERP entities.
    Supports Journal Entries, Invoices, Purchase Orders, etc.
    """
    FILE_TYPE_CHOICES = [
        ('PDF', 'PDF Document'),
        ('IMAGE', 'Image'),
        ('SPREADSHEET', 'Spreadsheet'),
        ('DOCUMENT', 'Word/Text Document'),
        ('OTHER', 'Other'),
    ]
    
    company = models.ForeignKey('company.CompanyProfile', on_delete=models.CASCADE)
    
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    file = models.FileField(upload_to='documents/%Y/%m/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='OTHER')
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="Size in bytes")
    
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_attachments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("document attachment")
        verbose_name_plural = _("document attachments")
    
    def __str__(self):
        return f"{self.filename} ({self.content_object})"
    
    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        if self.filename and not self.filename:
            self.filename = self.file.name
        super().save(*args, **kwargs)
