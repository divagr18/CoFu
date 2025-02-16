from django import forms

class BusinessModelInputForm(forms.Form):
    industry = forms.CharField(
        label="Enter the industry:",
        max_length=255,
        help_text="e.g., 'e-commerce', 'fintech', 'healthcare'"
    )
    target_market = forms.CharField(
        label="Describe the target market:",
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 60}),
        help_text="e.g., 'Small businesses in the US', 'Millennials in Europe'"
    )
    business_description = forms.CharField(
        label="Describe your business idea:",
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 60}),
        help_text="Provide a detailed description of your business concept"
    )