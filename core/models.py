from __future__ import annotations

from typing import Iterable, Optional

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Lightweight, extensible models for a 5e-style character system.
# See core/character.md for the broader data model vision. This file provides
# the core entities to create characters with abilities, classes, skills, and
# common lookups (species, languages, backgrounds, feats, spells, items).


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Language(TimeStampedModel):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, default="")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Skill(TimeStampedModel):
    ABILITY_CHOICES = [
        ("str", "Strength"),
        ("dex", "Dexterity"),
        ("con", "Constitution"),
        ("int", "Intelligence"),
        ("wis", "Wisdom"),
        ("cha", "Charisma"),
    ]

    name = models.CharField(max_length=64, unique=True)
    ability = models.CharField(max_length=3, choices=ABILITY_CHOICES)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.name} ({self.get_ability_display()})"


class Species(TimeStampedModel):
    SIZE_CHOICES = [
        ("tiny", "Tiny"),
        ("small", "Small"),
        ("medium", "Medium"),
        ("large", "Large"),
    ]

    name = models.CharField(max_length=64, unique=True)
    speed = models.PositiveSmallIntegerField(default=30)
    size = models.CharField(max_length=8, choices=SIZE_CHOICES, default="medium")
    alignment = models.TextField(blank=True, default="")
    age = models.TextField(blank=True, default="")
    languages = models.ManyToManyField(Language, blank=True, related_name="species")
    # Arbitrary extensibility: bonuses, traits, options, etc.
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        verbose_name_plural = "species"
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Subrace(TimeStampedModel):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name="subraces")
    name = models.CharField(max_length=64)
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        unique_together = ("species", "name")
        ordering = ["species__name", "name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.species}: {self.name}"


class Background(TimeStampedModel):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, default="")
    languages = models.ManyToManyField(Language, blank=True, related_name="backgrounds")
    # Optional: backgrounds often grant two fixed skill proficiencies
    skills = models.ManyToManyField(Skill, blank=True, related_name="backgrounds")
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Feat(TimeStampedModel):
    name = models.CharField(max_length=96, unique=True)
    description = models.TextField()
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Class(TimeStampedModel):
    name = models.CharField(max_length=64, unique=True)
    hit_die = models.PositiveSmallIntegerField(default=8)
    # e.g., ["str", "con"] for Barbarian
    saving_throws = models.JSONField(blank=True, default=list)
    # Example: {"choose": 2, "from": [skill_ids...]}
    skill_proficiency_options = models.JSONField(blank=True, default=dict)
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        verbose_name_plural = "classes"
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Subclass(TimeStampedModel):
    parent_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="subclasses")
    name = models.CharField(max_length=64)
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        unique_together = ("parent_class", "name")
        ordering = ["parent_class__name", "name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.parent_class}: {self.name}"


class Spell(TimeStampedModel):
    name = models.CharField(max_length=96, unique=True)
    level = models.PositiveSmallIntegerField(default=0)
    school = models.CharField(max_length=32, blank=True, default="")
    casting_time = models.CharField(max_length=64, blank=True, default="")
    range = models.CharField(max_length=64, blank=True, default="")
    components = models.CharField(max_length=64, blank=True, default="")
    duration = models.CharField(max_length=64, blank=True, default="")
    description = models.TextField(blank=True, default="")
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ["level", "name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.name} (Lv {self.level})"


class Item(TimeStampedModel):
    name = models.CharField(max_length=96, unique=True)
    category = models.CharField(max_length=48, blank=True, default="")
    weight = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, default="")
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Character(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="characters")
    name = models.CharField(max_length=96)

    # Lineage and story
    species = models.ForeignKey(Species, on_delete=models.SET_NULL, null=True, blank=True, related_name="characters")
    subrace = models.ForeignKey(Subrace, on_delete=models.SET_NULL, null=True, blank=True, related_name="characters")
    background = models.ForeignKey(Background, on_delete=models.SET_NULL, null=True, blank=True, related_name="characters")

    # Ability scores (1..30)
    str_score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)], default=10)
    dex_score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)], default=10)
    con_score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)], default=10)
    int_score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)], default=10)
    wis_score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)], default=10)
    cha_score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)], default=10)

    alignment = models.CharField(max_length=32, blank=True, default="")
    xp = models.PositiveIntegerField(default=0)
    inspiration = models.BooleanField(default=False)

    # Hit points (current state tracked here).
    hp_current = models.IntegerField(default=0)
    hp_temp = models.IntegerField(default=0)

    # Finalized languages and feats chosen for this character
    languages = models.ManyToManyField(Language, blank=True, related_name="characters")
    feats = models.ManyToManyField(Feat, blank=True, related_name="characters")

    # Misc extensibility: coins, notes, UI toggles, custom flags, etc.
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        indexes = [models.Index(fields=["user", "name"])]
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.name}"

    # ---- Derived values & helpers ----
    @staticmethod
    def ability_modifier(score: int) -> int:
        return (score - 10) // 2

    @property
    def level_total(self) -> int:
        agg = self.classes.aggregate(total=models.Sum("level"))
        return int(agg["total"] or 0)

    @property
    def proficiency_bonus(self) -> int:
        lvl = self.level_total
        if lvl <= 0:
            return 2
        if lvl <= 4:
            return 2
        if lvl <= 8:
            return 3
        if lvl <= 12:
            return 4
        if lvl <= 16:
            return 5
        return 6

    def ability_score(self, ability: str) -> int:
        ability = ability.lower()
        return {
            "str": self.str_score,
            "dex": self.dex_score,
            "con": self.con_score,
            "int": self.int_score,
            "wis": self.wis_score,
            "cha": self.cha_score,
        }[ability]

    def ability_mod(self, ability: str) -> int:
        return self.ability_modifier(self.ability_score(ability))

    # Skill proficiency: 0 = none, 1 = proficient, 2 = expertise
    def skill_proficiency_level(self, skill: Skill | int) -> int:
        skill_id = skill.pk if isinstance(skill, Skill) else int(skill)
        rel = self.skill_links.filter(skill_id=skill_id).first()
        if not rel:
            return 0
        return 2 if rel.expertise else 1

    def skill_modifier(self, skill: Skill) -> int:
        base = self.ability_mod(skill.ability)
        prof_level = self.skill_proficiency_level(skill)
        return base + (self.proficiency_bonus * prof_level)

    def proficient_saving_throws(self) -> set[str]:
        profs: set[str] = set()
        for cc in self.classes.select_related("clazz").all():
            for ab in (cc.clazz.saving_throws or []):
                profs.add(ab)
        return profs

    def saving_throw_modifier(self, ability: str) -> int:
        base = self.ability_mod(ability)
        return base + (self.proficiency_bonus if ability in self.proficient_saving_throws() else 0)


class CharacterClass(TimeStampedModel):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="classes")
    clazz = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="character_memberships")
    subclass = models.ForeignKey(Subclass, on_delete=models.SET_NULL, null=True, blank=True, related_name="character_memberships")
    level = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)], default=1)
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ("character", "clazz")
        indexes = [models.Index(fields=["character", "clazz"])]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.character} - {self.clazz} {self.level}"


class CharacterSkill(TimeStampedModel):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="skill_links")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="character_links")
    expertise = models.BooleanField(default=False)

    class Meta:
        unique_together = ("character", "skill")
        indexes = [models.Index(fields=["character", "skill"])]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.character} - {self.skill} ({'Expertise' if self.expertise else 'Proficient'})"


class CharacterItem(TimeStampedModel):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="character_items")
    quantity = models.PositiveIntegerField(default=1)
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        unique_together = ("character", "item")
        indexes = [models.Index(fields=["character", "item"])]


class CharacterSpell(TimeStampedModel):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="spells")
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE, related_name="character_spells")
    known = models.BooleanField(default=True)
    prepared = models.BooleanField(default=False)
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        unique_together = ("character", "spell")
        indexes = [models.Index(fields=["character", "spell"])]
