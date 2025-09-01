from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class DiceSettingsForm(forms.ModelForm):
    dice_external_theme_url = forms.URLField(
        required=False,
        label="External theme URL",
        help_text=(
            "Optional: URL to a DiceBox-compatible theme folder (must contain theme.config.json). "
            "GitHub is supported — use a folder URL like "
            "https://github.com/<user>/<repo>/tree/<branch>/<path-to-theme>."
        ),
        widget=forms.URLInput(attrs={"placeholder": "https://…/mytheme"}),
    )

    class Meta:
        model = User
        fields = ("dice_preset", "dice_finish", "dice_external_theme_url")
        widgets = {
            "dice_preset": forms.Select(attrs={"class": "select"}),
            "dice_finish": forms.Select(attrs={"class": "select"}),
        }
