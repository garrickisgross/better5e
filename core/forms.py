from __future__ import annotations

from django import forms

from .models import Feat, Class, Species


class FeatForm(forms.ModelForm):
    prerequisite_class = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
    )
    prerequisite_class_level = forms.IntegerField(
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
    )
    prerequisite_feature = forms.ModelChoiceField(
        queryset=Feat.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
    )
    prerequisite_total_level = forms.IntegerField(
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
    )
    prerequisite_species = forms.ModelChoiceField(
        queryset=Species.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
    )
    charges = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
    )
    recharge_type = forms.CharField(
        max_length=64,
        required=False,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full"}),
    )
    grants = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Feat
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "description": forms.Textarea(
                attrs={"class": "textarea textarea-bordered w-full", "rows": 4}
            ),
        }

    def save(self, commit: bool = True) -> Feat:
        feat = super().save(commit=False)
        data: dict = {}
        cd = self.cleaned_data
        prereq = {}
        if cd.get("prerequisite_class") and cd.get("prerequisite_class_level"):
            prereq["class"] = cd["prerequisite_class"].id
            prereq["class_level"] = cd["prerequisite_class_level"]
        if cd.get("prerequisite_feature"):
            prereq["feature"] = cd["prerequisite_feature"].id
        if cd.get("prerequisite_total_level"):
            prereq["total_level"] = cd["prerequisite_total_level"]
        if cd.get("prerequisite_species"):
            prereq["species"] = cd["prerequisite_species"].id
        if prereq:
            data["prerequisites"] = prereq
        if cd.get("charges") is not None:
            data["charges"] = cd["charges"]
        if cd.get("recharge_type"):
            data["recharge_type"] = cd["recharge_type"]
        import json

        if cd.get("grants"):
            try:
                data["grants"] = json.loads(cd["grants"])
            except Exception:
                pass
        feat.data = data
        if commit:
            feat.save()
        return feat
