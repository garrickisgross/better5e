from collections import defaultdict
from django.conf import settings
from django.db import models
from django.db.models import Sum, Q, Manager
from django.forms import ValidationError
from typing import TYPE_CHECKING, Optional


# Provide a lightweight, type-checker-friendly alias for related managers
# without changing runtime behavior or incurring heavy imports.
if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager as _RelatedManager
else:
    _RelatedManager = Manager  # type: ignore[assignment]

# TODO Keep this helper to handle future type-checking issues gracefully.

class Named(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class CharacterClass(Named):
    hit_die = models.PositiveSmallIntegerField(default=8)
    # TODO finish implementing class, spec can be found in class.md

class Subclass(CharacterClass):
    parent_class = models.ForeignKey("core.CharacterClass", on_delete=models.CASCADE, related_name="subclasses")
    # Note: Multi-table inheritance prevents adding a constraint over parent's fields here.


class Origin(Named):
    #TODO implement Origin, spec can be found in origin.md
    pass

class Background(Named):
    #TODO implement Background, spec can be found in background.md
    pass

class Species(Named):
    #TODO implement Species, spec can be found in species.md
    pass

class Feature(Named):
    class Category(models.TextChoices):
        ORIGIN = "origin", "Origin"
        BACKGROUND = "background", "Background"
        CLASS = "class", "Class"
        SUBCLASS = "subclass", "Subclass"
        SPECIES = "species", "Species"
        OTHER = "other", "Other"

    class Recharge(models.TextChoices):
        NONE = "none", "None"
        SHORT_REST = "short_rest", "Short Rest"
        LONG_REST = "long_rest", "Long Rest"
        DAILY_DAWN = "daily_dawn", "Daily (Dawn)"
        DAILY_DUSK = "daily_dusk", "Daily (Dusk)"

    # Optional categorization to help determine source/origin
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        blank=True,
        default="",
        help_text="Optional feature category (origin, background, class, etc).",
    )

    # Narrative/body description
    description = models.TextField(blank=True, default="")

    # Flexible payload describing what this feature grants.
    # Stored as JSON for extensibility: e.g. {"grants": [{"type": "proficiency", ...}]}
    benefit = models.JSONField(default=dict, blank=True)

    # Limited use tracking blueprint
    max_charges = models.PositiveSmallIntegerField(null=True, blank=True)
    recharge = models.CharField(
        max_length=20,
        choices=Recharge.choices,
        blank=True,
        default="",
        help_text="When limited uses recharge.",
    )

    # Prerequisites for automatic mounting based on character makeup
    min_level = models.PositiveSmallIntegerField(default=1)
    requires_class = models.ForeignKey(
        "core.CharacterClass",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="features_requiring_class",
    )
    requires_subclass = models.ForeignKey(
        "core.Subclass",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="features_requiring_subclass",
    )
    requires_origin = models.ForeignKey(
        "core.Origin",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="granted_features",
    )
    requires_background = models.ForeignKey(
        "core.Background",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="granted_features",
    )
    requires_species = models.ForeignKey(
        "core.Species",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="granted_features",
    )

    class Meta:  # type: ignore
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["min_level"]),
        ]

    def clean(self) -> None:
        # If a subclass is required, ensure it matches the required class when provided
        if self.requires_subclass and self.requires_class:
            if self.requires_subclass.parent_class_id != self.requires_class_id:
                raise ValidationError(
                    "requires_subclass: Subclass does not belong to the required class"
                )

        # If recharge specified, feature should have max_charges
        if self.recharge and not self.max_charges:
            raise ValidationError("recharge: requires max_charges to be set")

    @property
    def is_limited_use(self) -> bool:
        return bool(self.max_charges)


class CharacterFeature(models.Model):
    """Join model capturing per-character feature state (e.g., charges)."""
    character = models.ForeignKey(
        "core.Character",
        on_delete=models.CASCADE,
        related_name="character_features",
    )
    feature = models.ForeignKey(
        "core.Feature",
        on_delete=models.CASCADE,
        related_name="character_features",
    )
    current_charges = models.PositiveSmallIntegerField(null=True, blank=True)
    state = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["character", "feature"], name="uq_char_feature_once"),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.character} -> {self.feature}"

class Item(Named):
    #TODO implement Item, spec can be found in item.md
    pass


class Character(models.Model):
    if TYPE_CHECKING:
        class_levels: "_RelatedManager[CharacterClassLevel]"
        features: "_RelatedManager[Feature]"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="characters",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    level = models.PositiveSmallIntegerField(default=1)
    exp = models.PositiveIntegerField(default=0)

    # Features currently attached to this character
    features = models.ManyToManyField(
        "core.Feature",
        through="core.CharacterFeature",
        related_name="characters",
        blank=True,
    )

    origin = models.ForeignKey(
        "core.Origin",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="characters",
    )

    background = models.ForeignKey(
        "core.Background",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="characters"   
    )
    
    class Meta:
        ordering = ["-updated_at", "name"],
        unique_together = [("owner", "name")]

    def __str__(self):
        return f"{self.name} - {self.total_level}"
    
    @property
    def total_level(self):
        agg = self.class_levels.aggregate(total=Sum("levels")) # type: ignore
        return agg["total"] or 0
    
    @property
    def classes_summary(self) -> str:
        """
        e.g., 'F4/W3' by summing levels per class.
        """
        levels = defaultdict(int)
        #TODO fix type checking here or adjust code as needed so lsp doesn't highlight error. 
        for row in self.class_levels.select_related("character_class").only(
            "character_class__name", "levels"
        ):
            # FK is non-null (PROTECT), so mypy/pyright are fine with attribute access
            name = row.character_class.name
            levels[name] += row.levels

        parts = [f"{name}{lvl}" for name, lvl in sorted(levels.items())]
        return "/".join(parts) if parts else "—"
    
    @staticmethod
    def ability_mod(score: int) -> int:
        return (score - 10) // 2
    
    #TODO Determine if a custom clean function is needed, and implement. 

    def save(self, *args, **kwargs):
        self.full_clean()  # enforce clean() on save, including in admin/shell
        return super().save(*args, **kwargs)

    # Feature mounting helpers
    def can_mount_feature(self, feature: "Feature") -> bool:
        # Level gate
        if feature.min_level and self.total_level < feature.min_level:
            return False

        # Origin/background/species gates (species not yet on Character; skip if required)
        if feature.requires_origin_id and self.origin_id != feature.requires_origin_id:
            return False
        if feature.requires_background_id and self.background_id != feature.requires_background_id:
            return False
        # If requires_species is set but Character lacks species, conservatively disallow
        if feature.requires_species_id is not None:
            # Character has no species field currently; reject since requirement can't be satisfied
            return False

        # Class gate
        if feature.requires_class_id:
            if not self.class_levels.filter(character_class_id=feature.requires_class_id).exists():
                return False

        # Subclass gate
        if feature.requires_subclass_id:
            if not self.class_levels.filter(subclass_id=feature.requires_subclass_id).exists():
                return False

        return True

    def mount_feature(self, feature: "Feature") -> "CharacterFeature":
        if not self.can_mount_feature(feature):
            raise ValidationError("Character does not meet prerequisites for this feature")

        # Idempotent mount: return existing row if present
        cf, created = CharacterFeature.objects.get_or_create(
            character=self, feature=feature,
            defaults={
                "current_charges": feature.max_charges if feature.max_charges is not None else None,
            },
        )
        # If created is False but feature has charges and current_charges is None, top it up
        if not created and feature.max_charges is not None and cf.current_charges is None:
            cf.current_charges = feature.max_charges
            cf.save(update_fields=["current_charges"])
        return cf
    

class CharacterClassLevel(models.Model):
    if TYPE_CHECKING:
        subclass_id: Optional[int]
        character_class_id: Optional[int]
        character_class_name: Optional[str]

    character = models.ForeignKey(
        "core.Character",
        on_delete=models.CASCADE,
        related_name="class_levels"
    )

    character_class = models.ForeignKey(
        "core.CharacterClass",
        on_delete=models.PROTECT,
        related_name="character_levels"
    )

    subclass = models.ForeignKey(
        "core.Subclass",
        on_delete=models.PROTECT,
        related_name="subclass_levels"
    )

    levels = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["character", "character_class"], name="uq_char_one_row_per_class"),
            models.CheckConstraint(check=Q(levels__gte=1), name="ck_levels_gte_1")
        ]

    def __str__(self):
        sub = f" / {self.subclass}" if self.subclass else ""
        return f"{self.character} -> {self.character_class} {self.levels}{sub}"
    
    def clean(self) -> None:
        if self.subclass and self.subclass.parent_class_id != self.character_class_id:
            raise ValidationError("subclass: Subclass does not belong to selected class")
    
    
