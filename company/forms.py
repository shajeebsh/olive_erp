from django import forms
from .models import CompanyProfile

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['name', 'address', 'phone', 'email', 'website', 'tax_id', 'fiscal_year_start_date', 'default_currency']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Olive Tech Solutions Ltd'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full business address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 234 567 8900'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@company.com'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.company.com'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tax/VAT Number'}),
            'fiscal_year_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'default_currency': forms.Select(attrs={'class': 'form-select'}),
        }
