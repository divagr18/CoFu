from django import forms

class MarketSizeInputForm(forms.Form):
    industry = forms.CharField(
        label="Enter the industry:",
        max_length=255,
        help_text="e.g., 'e-commerce', 'fintech', 'healthcare'"
    )
    region = forms.CharField(
        label="Enter the region:",
        max_length=255,
        help_text="e.g., 'United States', 'Europe', 'Asia'"
    )
    target_market = forms.CharField(
        label="Describe the target market:",
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 60}),
        help_text="e.g., 'Small businesses in the US', 'Millennials in Europe'"
    )
    customer_segment = forms.CharField(
        label="Customer segment (optional):",
        max_length=255,
        required=False,
        help_text="e.g., 'B2B', 'B2C', 'SaaS'"
    )
    average_selling_price = forms.FloatField(
        label="Average selling price (optional):",
        required=False,
        help_text="Enter the average price of your product/service in USD"
    )