from django import forms
from tax_engine.countries.ie.models import Director, Secretary, Shareholder
from tax_engine.countries.ie.rbo import BeneficialOwner

COUNTRY_CHOICES = [
    ('', '--- Select Country ---'),
    ('Ireland', 'Ireland'),
    ('United Kingdom', 'United Kingdom'),
    ('United States', 'United States'),
    ('Germany', 'Germany'),
    ('France', 'France'),
    ('Netherlands', 'Netherlands'),
    ('Belgium', 'Belgium'),
    ('Spain', 'Spain'),
    ('Italy', 'Italy'),
    ('Portugal', 'Portugal'),
    ('Poland', 'Poland'),
    ('Sweden', 'Sweden'),
    ('Norway', 'Norway'),
    ('Denmark', 'Denmark'),
    ('Finland', 'Finland'),
    ('Switzerland', 'Switzerland'),
    ('Austria', 'Austria'),
    ('Canada', 'Canada'),
    ('Australia', 'Australia'),
    ('New Zealand', 'New Zealand'),
    ('Japan', 'Japan'),
    ('China', 'China'),
    ('India', 'India'),
    ('Singapore', 'Singapore'),
    ('Hong Kong', 'Hong Kong'),
    ('United Arab Emirates', 'United Arab Emirates'),
    ('Other', 'Other'),
]

NATIONALITY_CHOICES = [
    ('', '--- Select Nationality ---'),
    ('Irish', 'Irish'),
    ('British', 'British'),
    ('American', 'American'),
    ('German', 'German'),
    ('French', 'French'),
    ('Dutch', 'Dutch'),
    ('Belgian', 'Belgian'),
    ('Spanish', 'Spanish'),
    ('Italian', 'Italian'),
    ('Portuguese', 'Portuguese'),
    ('Polish', 'Polish'),
    ('Swedish', 'Swedish'),
    ('Norwegian', 'Norwegian'),
    ('Danish', 'Danish'),
    ('Finnish', 'Finnish'),
    ('Swiss', 'Swiss'),
    ('Austrian', 'Austrian'),
    ('Canadian', 'Canadian'),
    ('Australian', 'Australian'),
    ('New Zealander', 'New Zealander'),
    ('Japanese', 'Japanese'),
    ('Chinese', 'Chinese'),
    ('Indian', 'Indian'),
    ('Singaporean', 'Singaporean'),
    ('Hong Kong', 'Hong Kong'),
    ('UAE', 'UAE'),
    ('Other', 'Other'),
]


class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = [
            'first_name', 'last_name', 'former_names',
            'pps_number', 'date_of_birth', 'nationality',
            'address_line1', 'address_line2', 'city', 'county', 'country', 'country_code',
            'appointment_date',
            'is_executive', 'is_chairperson', 'other_directorships'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'former_names': forms.TextInput(attrs={'class': 'form-control'}),
            'pps_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567AB'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nationality': forms.Select(attrs={'class': 'form-select'}, choices=NATIONALITY_CHOICES),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'county': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-select'}, choices=COUNTRY_CHOICES),
            'country_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IE'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_executive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_chairperson': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'other_directorships': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DirectorEditForm(forms.ModelForm):
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
            'nationality': forms.Select(attrs={'class': 'form-select'}, choices=NATIONALITY_CHOICES),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'county': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-select'}, choices=COUNTRY_CHOICES),
            'country_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IE'}),
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
            'appointment_date'
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
            'country': forms.Select(attrs={'class': 'form-select'}, choices=COUNTRY_CHOICES),
            'country_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IE'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class SecretaryEditForm(forms.ModelForm):
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
            'country': forms.Select(attrs={'class': 'form-select'}, choices=COUNTRY_CHOICES),
            'country_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IE'}),
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
            'country': forms.Select(attrs={'class': 'form-select'}, choices=COUNTRY_CHOICES),
            'country_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IE'}),
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
            'nationality': forms.Select(attrs={'class': 'form-select'}, choices=NATIONALITY_CHOICES),
            'pps_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'county': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-select'}, choices=COUNTRY_CHOICES),
            'country_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IE'}),
            'interest_type': forms.Select(attrs={'class': 'form-select'}),
            'interest_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'shares_held': forms.NumberInput(attrs={'class': 'form-control'}),
            'percentage_held': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'voting_rights_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'became_owner_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ceased_owner_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }