from models.character import Character
from repos.character import CharacterRepo

class CharacterController:
    @staticmethod
    def create_character(character_data: dict) -> int:
        character_instance = Character(**character_data)
        return CharacterRepo.create(character_instance)

    @staticmethod
    def get_character(character_id: int) -> Character:
        return CharacterRepo.get(character_id)

    @staticmethod
    def list_characters() -> list[Character]:
        return CharacterRepo.list_all()

    @staticmethod
    def update_character(character_id: int, updates: dict) -> None:
        CharacterRepo.update(character_id, updates)

    @staticmethod
    def delete_character(character_id: int) -> None:
        CharacterRepo.delete(character_id)