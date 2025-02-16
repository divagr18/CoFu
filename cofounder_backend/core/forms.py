from django import forms

class PromptForm(forms.Form):
    text = forms.CharField(label='Enter your prompt', widget=forms.Textarea)