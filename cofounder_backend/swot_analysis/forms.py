from django import forms

class SWOTInputForm(forms.Form):
    business_description = forms.CharField(
        label="Describe your business idea:",
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 60})
    )
    industry = forms.CharField(
        label="Enter the industry:",
        max_length=255,
        help_text="e.g., 'e-commerce', 'fintech', 'healthcare'"
    )