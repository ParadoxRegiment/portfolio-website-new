from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "input w-full", "autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="Your email",
        widget=forms.EmailInput(attrs={"class": "input w-full", "autocomplete": "email"}),
    )
    message = forms.CharField(
        max_length=5000,
        widget=forms.Textarea(attrs={"class": "textarea w-full", "rows": 6}),
    )
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )
    leave_empty = forms.CharField(
        required=False,
        label="Leave this field empty",
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )
    
    def is_spam(self) -> bool:
        return bool(self.cleaned_data.get("leave_empty"))