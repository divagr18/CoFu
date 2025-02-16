from django import forms

class CompetitorAnalysisInputForm(forms.Form):
    competitor_1 = forms.CharField(
        label="Competitor 1 (Name or Website):",
        max_length=255,
        help_text="Enter the name or website URL of your first competitor",
        required=True
    )
    competitor_2 = forms.CharField(
        label="Competitor 2 (Name or Website):",
        max_length=255,
        required=False,
        help_text="Enter the name or website URL of your second competitor (optional)"
    )
    competitor_3 = forms.CharField(
        label="Competitor 3 (Name or Website):",
        max_length=255,
        required=False,
        help_text="Enter the name or website URL of your third competitor (optional)"
    )