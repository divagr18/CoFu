from django import forms

class NewsOverviewInputForm(forms.Form):
    sector = forms.CharField(
        label="Enter the sector:",
        max_length=255,
        help_text="e.g., 'e-commerce', 'fintech', 'healthcare'"
    )