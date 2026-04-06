from django import forms
from .models import Dividend, RelatedPartyTransaction

class DividendForm(forms.ModelForm):
    class Meta:
        model = Dividend
        fields = [
            'shareholder_name', 'declaration_date', 'payment_date', 
            'dividend_per_share', 'number_of_shares', 'net_amount', 
            'tax_credit', 'voucher_number', 'is_paid'
        ]
        widgets = {
            'shareholder_name': forms.TextInput(attrs={'class': 'form-control'}),
            'declaration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'dividend_per_share': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'number_of_shares': forms.NumberInput(attrs={'class': 'form-control'}),
            'net_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'tax_credit': forms.NumberInput(attrs={'class': 'form-control'}),
            'voucher_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RelatedPartyTransactionForm(forms.ModelForm):
    class Meta:
        model = RelatedPartyTransaction
        fields = [
            'party_name', 'relationship', 'transaction_date', 
            'transaction_nature', 'amount', 'is_arm_length', 'disclosure_required'
        ]
        widgets = {
            'party_name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Director, Parent Company'}),
            'transaction_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'transaction_nature': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Loan, Management Fees'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_arm_length': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'disclosure_required': forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': 'checked'}),
        }
