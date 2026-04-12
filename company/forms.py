from django import forms

from .models import CompanyProfile, Currency


class CompanyProfileForm(forms.ModelForm):
    default_currency = forms.ModelChoiceField(
        queryset=Currency.objects.filter(is_active=True),
        empty_label="--- Select Currency ---",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = CompanyProfile
        fields = [
            "name",
            "address",
            "phone",
            "email",
            "website",
            "tax_id",
            "fiscal_year_start_date",
            "default_currency",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Default Company Ltd",
                }
            ),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "tax_id": forms.TextInput(attrs={"class": "form-control"}),
            "fiscal_year_start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if Currency.objects.count() == 0:
            self.fields["default_currency"].queryset = Currency.objects.none()
            self.fields["default_currency"].help_text = (
                "No currencies available. Run: python manage.py create_initial_data"
            )


class FeatureSelectionForm(forms.Form):
    country = forms.CharField(max_length=2)
