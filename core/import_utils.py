"""
Bulk Import Utilities for OliveERP

Provides a foundation for CSV/XLSX imports for master data:
- Chart of Accounts
- Products
- Customers
- Suppliers

Usage:
1. Subclass BaseBulkImport in your module
2. Define field_mapping and validation rules
3. Call import_data() with CSV file
"""
import csv
import logging
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple, Any
from django.db import transaction

logger = logging.getLogger(__name__)


class ImportResult:
    """Result of a bulk import operation."""
    
    def __init__(self):
        self.success_count = 0
        self.error_count = 0
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.created_ids: List[int] = []
        self.updated_ids: List[int] = []
    
    @property
    def is_valid(self) -> bool:
        return self.error_count == 0
    
    def add_error(self, row: int, message: str):
        self.errors.append(f"Row {row}: {message}")
        self.error_count += 1
    
    def add_warning(self, row: int, message: str):
        self.warnings.append(f"Row {row}: {message}")
    
    def __str__(self):
        return f"ImportResult: {self.success_count} success, {self.error_count} errors, {self.warnings} warnings"


class FieldValidator:
    """Helper class for validating individual fields."""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> Optional[str]:
        if value is None or (isinstance(value, str) and not value.strip()):
            return f"Required field '{field_name}' is missing"
        return None
    
    @staticmethod
    def validate_decimal(value: str, field_name: str, allow_null: bool = True) -> Optional[Decimal]:
        if not value or not value.strip():
            if allow_null:
                return None
            return f"Field '{field_name}' must be a valid number"
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError):
            return f"Field '{field_name}' is not a valid number: {value}"
    
    @staticmethod
    def validate_email(value: str, field_name: str) -> Optional[str]:
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if value and not re.match(pattern, value):
            return f"Field '{field_name}' is not a valid email: {value}"
        return None
    
    @staticmethod
    def validate_choice(value: str, choices: List[str], field_name: str) -> Optional[str]:
        if value and value.upper() not in [c.upper() for c in choices]:
            return f"Field '{field_name}' has invalid value: {value}. Valid: {', '.join(choices)}"
        return None


class BaseBulkImport:
    """
    Base class for bulk imports.
    
    Subclasses should define:
    - model: The Django model to import to
    - required_fields: List of required field names
    - field_mapping: Dict mapping CSV headers to model fields
    - unique_fields: Fields that uniquely identify records for updates
    """
    
    model = None
    required_fields: List[str] = []
    field_mapping: Dict[str, str] = {}
    unique_fields: List[str] = ['code']
    
    def __init__(self, company=None, user=None):
        self.company = company
        self.user = user
        self.validator = FieldValidator()
    
    def import_data(self, csv_file, create_only: bool = False) -> ImportResult:
        """
        Import data from a CSV file.
        
        Args:
            csv_file: File-like object containing CSV data
            create_only: If True, skip updates to existing records
            
        Returns:
            ImportResult with success/error counts and details
        """
        result = ImportResult()
        
        try:
            reader = csv.DictReader(csv_file)
            headers = reader.fieldnames
            
            # Validate required columns
            missing_cols = set(self.required_fields) - set(headers)
            if missing_cols:
                result.add_error(0, f"Missing required columns: {', '.join(missing_cols)}")
                return result
            
            rows = list(reader)
            total = len(rows)
            logger.info(f"Starting bulk import of {total} rows for {self.model.__name__}")
            
            with transaction.atomic():
                for idx, row in enumerate(rows, start=1):
                    try:
                        self._process_row(row, result, create_only)
                    except Exception as e:
                        logger.exception(f"Error processing row {idx}")
                        result.add_error(idx, str(e))
            
            logger.info(f"Bulk import complete: {result.success_count} success, {result.error_count} errors")
            
        except Exception as e:
            logger.exception("Failed to parse CSV file")
            result.add_error(0, f"Failed to parse CSV: {str(e)}")
        
        return result
    
    def _process_row(self, row: Dict, result: ImportResult, create_only: bool):
        """Process a single row from the CSV."""
        # Build cleaned data from row
        cleaned = self._clean_row(row)
        
        # Validate
        errors = self._validate_row(cleaned)
        if errors:
            for error in errors:
                result.add_error(0, error)
            return
        
        # Find or create
        obj = self._find_existing(cleaned)
        if obj:
            if create_only:
                result.add_warning(0, f"Skipped existing record: {cleaned.get('code', 'N/A')}")
                return
            self._update_object(obj, cleaned)
            result.updated_ids.append(obj.pk)
        else:
            obj = self._create_object(cleaned)
            result.created_ids.append(obj.pk)
        
        result.success_count += 1
    
    def _clean_row(self, row: Dict) -> Dict:
        """Clean and map row data to model fields."""
        cleaned = {}
        for csv_header, model_field in self.field_mapping.items():
            value = row.get(csv_header, '').strip()
            if value:
                cleaned[model_field] = value
        return cleaned
    
    def _validate_row(self, cleaned: Dict) -> List[str]:
        """Validate a cleaned row. Return list of error messages."""
        errors = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in cleaned or not cleaned[field]:
                errors.append(f"Required field '{field}' is missing")
        
        return errors
    
    def _find_existing(self, cleaned: Dict):
        """Find existing object by unique fields."""
        if not self.model:
            return None
            
        filters = {}
        for field in self.unique_fields:
            if field in cleaned:
                filters[field] = cleaned[field]
        
        if not filters:
            return None
            
        try:
            return self.model.objects.get(**filters)
        except self.model.DoesNotExist:
            return None
        except self.model.MultipleObjectsReturned:
            return None
    
    def _create_object(self, cleaned: Dict):
        """Create a new model object."""
        if self.company:
            cleaned['company'] = self.company
        
        obj = self.model(**cleaned)
        obj.full_clean()
        obj.save()
        
        if self.user:
            logger.info(f"Created {self.model.__name__} {obj.pk} via bulk import by {self.user}")
        
        return obj
    
    def _update_object(self, obj, cleaned: Dict):
        """Update an existing model object."""
        for field, value in cleaned.items():
            setattr(obj, field, value)
        
        obj.full_clean()
        obj.save()
        
        if self.user:
            logger.info(f"Updated {self.model.__name__} {obj.pk} via bulk import by {self.user}")


class AccountBulkImport(BaseBulkImport):
    """Bulk import for Chart of Accounts."""
    
    from finance.models import Account
    
    model = Account
    required_fields = ['code', 'name']
    field_mapping = {
        'Code': 'code',
        'Name': 'name',
        'Type': 'account_type',
        'Parent': 'parent_id',
        'Description': 'description',
        'Active': 'is_active',
    }
    unique_fields = ['code']
    
    ACCOUNT_TYPES = ['Asset', 'Liability', 'Equity', 'Income', 'Expense']
    
    def _validate_row(self, cleaned: Dict) -> List[str]:
        errors = super()._validate_row(cleaned)
        
        if 'account_type' in cleaned:
            if cleaned['account_type'] not in self.ACCOUNT_TYPES:
                errors.append(f"Invalid account type: {cleaned['account_type']}")
        
        if 'is_active' in cleaned:
            val = cleaned['is_active'].lower()
            if val in ('true', '1', 'yes'):
                cleaned['is_active'] = True
            elif val in ('false', '0', 'no'):
                cleaned['is_active'] = False
        
        return errors


class ProductBulkImport(BaseBulkImport):
    """Bulk import for Products."""
    
    from inventory.models import Product
    
    model = Product
    required_fields = ['name', 'sku']
    field_mapping = {
        'Name': 'name',
        'SKU': 'sku',
        'Category': 'category_id',
        'Description': 'description',
        'Unit Price': 'unit_price',
        'Cost Price': 'cost_price',
        'Reorder Level': 'reorder_level',
        'Active': 'is_active',
    }
    unique_fields = ['sku']
    
    def _validate_row(self, cleaned: Dict) -> List[str]:
        errors = super()._validate_row(cleaned)
        
        for field in ['unit_price', 'cost_price', 'reorder_level']:
            if field in cleaned:
                result = self.validator.validate_decimal(cleaned[field], field)
                if isinstance(result, str):  # It's an error message
                    errors.append(result)
                else:
                    cleaned[field] = result
        
        return errors


def import_accounts_csv(csv_file, company, user) -> ImportResult:
    """Convenience function to import accounts."""
    importer = AccountBulkImport(company=company, user=user)
    return importer.import_data(csv_file)


def import_products_csv(csv_file, company, user) -> ImportResult:
    """Convenience function to import products."""
    importer = ProductBulkImport(company=company, user=user)
    return importer.import_data(csv_file)