from __future__ import annotations

from django import forms

from .models import Feat, Class, Species, Skill, Subclass


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
    modifiers = forms.CharField(required=False, widget=forms.HiddenInput())

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
        if cd.get("modifiers"):
            try:
                mods = json.loads(cd["modifiers"]) or []
                # Expect list of {target, operation, value}
                if isinstance(mods, list):
                    data["modifiers"] = mods
            except Exception:
                pass
        feat.data = data
        if commit:
            feat.save()
        return feat


class ClassForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "textarea textarea-bordered w-full", "rows": 4}),
    )
    level_map = forms.CharField(required=False, widget=forms.HiddenInput())
    saving_throws = forms.MultipleChoiceField(
        choices=Skill.ABILITY_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select select-bordered w-full"}),
    )
    skill_choose = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
    )
    skill_options = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select select-bordered w-full"}),
    )

    class Meta:
        model = Class
        fields = ["name", "hit_die", "saving_throws"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "hit_die": forms.NumberInput(attrs={"class": "input input-bordered w-full", "min": 1}),
        }

    def save(self, commit: bool = True) -> Class:
        cls = super().save(commit=False)
        data: dict = {}
        cd = self.cleaned_data
        if cd.get("description"):
            data["description"] = cd["description"]
        if cd.get("level_map"):
            import json

            try:
                data["level_map"] = json.loads(cd["level_map"])
            except Exception:
                pass
        if cd.get("skill_choose") or cd.get("skill_options"):
            cls.skill_proficiency_options = {
                "choose": cd.get("skill_choose") or 0,
                "from": [s.id for s in cd.get("skill_options", [])],
            }
        cls.data = data
        if commit:
            cls.save()
        return cls


class SubclassForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "textarea textarea-bordered w-full", "rows": 4}),
    )
    level_map = forms.CharField(required=False, widget=forms.HiddenInput())
    hit_die_override = forms.IntegerField(
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
    )
    saving_throws = forms.MultipleChoiceField(
        choices=Skill.ABILITY_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select select-bordered w-full"}),
    )
    skill_choose = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
    )
    skill_options = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select select-bordered w-full"}),
    )

    class Meta:
        model = Subclass
        fields = ["parent_class", "name"]
        widgets = {
            "parent_class": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
        }

    def save(self, commit: bool = True) -> Subclass:
        sub = super().save(commit=False)
        data: dict = {}
        cd = self.cleaned_data
        if cd.get("description"):
            data["description"] = cd["description"]
        if cd.get("level_map"):
            import json

            try:
                data["level_map"] = json.loads(cd["level_map"])
            except Exception:
                pass
        if cd.get("hit_die_override"):
            data["hit_die_override"] = cd["hit_die_override"]
        if cd.get("saving_throws"):
            data["saving_throws"] = cd["saving_throws"]
        if cd.get("skill_choose") or cd.get("skill_options"):
            data["skill_proficiency_options"] = {
                "choose": cd.get("skill_choose") or 0,
                "from": [s.id for s in cd.get("skill_options", [])],
            }
        sub.data = data
        if commit:
            sub.save()
        return sub
