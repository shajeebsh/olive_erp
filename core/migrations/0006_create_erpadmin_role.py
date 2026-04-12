from django.db import migrations


def create_erpadmin_role(apps, schema_editor):
    Role = apps.get_model('core', 'Role')
    Permission = apps.get_model('auth', 'Permission')
    
    erp_role, created = Role.objects.get_or_create(
        name='ErpAdmin',
        defaults={'description': 'Full ERP access to all modules - Finance, Inventory, CRM, HR, Projects, Purchasing, Reporting, and Tax Compliance'}
    )
    
    erp_apps = [
        'company', 'finance', 'inventory', 'crm', 'hr', 
        'projects', 'purchasing', 'reporting', 'tax_engine'
    ]
    
    perms = Permission.objects.filter(
        content_type__app_label__in=erp_apps
    ).distinct()
    
    erp_role.permissions.set(perms)
    
    print(f"Created ErpAdmin role with {perms.count()} permissions")


def remove_erpadmin_role(apps, schema_editor):
    Role = apps.get_model('core', 'Role')
    Role.objects.filter(name='ErpAdmin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_add_document_attachment'),
    ]

    operations = [
        migrations.RunPython(create_erpadmin_role, remove_erpadmin_role),
    ]