from database import BaseRepo
from models.feature import Feature

class FeatureRepo(BaseRepo):
    TABLE = "features"
    MODEL = Feature
    JSON_COLS = ["granted_features", "granted_spells", "granted_items", "modifiers", "rollable", "options"]