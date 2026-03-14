from django import forms
from .models import (
    Invoice, JournalEntry, JournalEntryLine, Account,
    PriceList, DiscountRule, RecurringInvoice, CreditDebitNote
)


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'customer', 'invoice_template', 'issue_date', 'due_date', 'total_amount', 'tax_amount', 'status']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'invoice_template': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class PriceListForm(forms.ModelForm):
    class Meta:
        model = PriceList
        fields = ['name', 'customer_group', 'valid_from', 'valid_to', 'is_active', 'priority']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_group': forms.Select(attrs={'class': 'form-select'}),
            'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class DiscountRuleForm(forms.ModelForm):
    class Meta:
        model = DiscountRule
        fields = ['name', 'discount_type', 'value', 'customer_group', 'customer', 
                  'product', 'product_category', 'min_quantity', 'min_amount', 
                  'valid_from', 'valid_to', 'priority', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'customer_group': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'product_category': forms.Select(attrs={'class': 'form-select'}),
            'min_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RecurringInvoiceForm(forms.ModelForm):
    class Meta:
        model = RecurringInvoice
        fields = ['name', 'customer', 'invoice_template', 'frequency', 'interval', 
                  'start_date', 'end_date', 'next_invoice_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'invoice_template': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'interval': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CreditDebitNoteForm(forms.ModelForm):
    class Meta:
        model = CreditDebitNote
        fields = ['note_number', 'note_type', 'original_invoice', 'date', 'reason', 
                  'subtotal', 'tax_amount', 'total_amount']
        widgets = {
            'note_number': forms.TextInput(attrs={'class': 'form-control'}),
            'note_type': forms.Select(attrs={'class': 'form-select'}),
            'original_invoice': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['entry_number', 'date', 'description', 'is_posted']
        widgets = {
            'entry_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_posted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['code', 'name', 'account_type', 'group_type', 'parent', 
                  'opening_balance', 'opening_balance_date', 'notes']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
            'group_type': forms.Select(attrs={'class': 'form-select'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'opening_balance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Only show accounts from same company as parent
        if self.company:
            self.fields['parent'].queryset = Account.objects.filter(
                company=self.company,
                group_type__in=['Primary', 'Sub-group']
            )
    
    def clean_code(self):
        code = self.cleaned_data['code']
        if self.company and Account.objects.filter(
            company=self.company, code=code
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Account code already exists for this company")
        return code
