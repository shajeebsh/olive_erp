from django import forms
from tax_engine.countries.ie.models import Director, Secretary, Shareholder
from tax_engine.countries.ie.rbo import BeneficialOwner


class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = [
            'first_name', 'last_name', 'former_names',
            'pps_number', 'date_of_birth', 'nationality',
            'address_line1', 'address_line2', 'city', 'county', 'country', 'country_code',
            'appointment_date', 'resignation_date',
            'is_executive', 'is_chairperson', 'other_directorships'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'former_names': forms.TextInput(attrs={'class': 'form-control'}),
            'pps_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567AB'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'county': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'country_code': forms.TextInput(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resignation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_executive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_chairperson': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'other_directorships': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SecretaryForm(forms.ModelForm):
    class Meta:
        model = Secretary
        fields = [
            'is_corporate', 'first_name', 'last_name', 'corporate_name', 'registration_number',
            'address_line1', 'address_line2', 'city', 'county', 'country', 'country_code',
            'appointment_date', 'resignation_date'
        ]
        widgets = {
            'is_corporate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'corporate_name': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'county': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'country_code': forms.TextInput(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resignation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ShareholderForm(forms.ModelForm):
    class Meta:
        model = Shareholder
        fields = [
            'is_corporate', 'first_name', 'last_name', 'corporate_name', 'registration_number',
            'country_incorporation', 'address_line1', 'address_line2', 'city', 'county', 'country',
            'country_code', 'ordinary_shares_held', 'preference_shares_held', 'percentage_held',
            'date_joined'
        ]
        widgets = {
            'is_corporate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'corporate_name': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'country_incorporation': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'county': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'country_code': forms.TextInput(attrs={'class': 'form-control'}),
            'ordinary_shares_held': forms.NumberInput(attrs={'class': 'form-control'}),
            'preference_shares_held': forms.NumberInput(attrs={'class': 'form-control'}),
            'percentage_held': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'date_joined': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class BeneficialOwnerForm(forms.ModelForm):
    class Meta:
        model = BeneficialOwner
        fields = [
            'first_name', 'last_name', 'former_names', 'date_of_birth', 'nationality', 'pps_number',
            'address_line1', 'address_line2', 'city', 'county', 'country', 'country_code',
            'interest_type', 'interest_details', 'shares_held', 'percentage_held',
            'voting_rights_percentage', 'became_owner_date', 'ceased_owner_date'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'former_names': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'pps_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'county': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'country_code': forms.TextInput(attrs={'class': 'form-control'}),
            'interest_type': forms.Select(attrs={'class': 'form-select'}),
            'interest_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'shares_held': forms.NumberInput(attrs={'class': 'form-control'}),
            'percentage_held': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'voting_rights_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'became_owner_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ceased_owner_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }