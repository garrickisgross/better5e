from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    # Dice appearance preferences
    DICE_PRESETS = [
        ("amethyst", "Amethyst"),
        ("emerald", "Emerald"),
        ("ruby", "Ruby"),
        ("sapphire", "Sapphire"),
        ("obsidian", "Obsidian"),
        ("ivory", "Ivory"),
        ("gold", "Gold"),
        ("pumpkin", "Pumpkin"),
    ]
    DICE_FINISHES = [
        ("matte", "Matte"),
        ("glossy", "Glossy"),
        ("pearl", "Pearl"),
    ]

    dice_preset = models.CharField(max_length=24, choices=DICE_PRESETS, default="amethyst")
    dice_finish = models.CharField(max_length=16, choices=DICE_FINISHES, default="glossy")
    # Optional: path to a folder hosting a DiceBox-compatible theme (must contain theme.config.json)
    dice_external_theme_url = models.URLField(blank=True, default="")
