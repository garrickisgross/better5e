from typing import List, Any
from models.feature import Feature
from repos.feature import FeatureRepo

class FeatureController:
    @staticmethod
    def create_feature(feature_data: dict) -> int:
        feature = Feature(**feature_data)
        return FeatureRepo.create(feature)

    @staticmethod
    def get_feature(feature_id: int) -> Feature:
        return FeatureRepo.get(feature_id)

    @staticmethod
    def list_features() -> List[Feature]:
        return FeatureRepo.list_all()

    @staticmethod
    def update_feature(feature_id: int, updates: dict) -> None:
        FeatureRepo.update(feature_id, updates)

    @staticmethod
    def delete_feature(feature_id: int) -> None:
        FeatureRepo.delete(feature_id)



