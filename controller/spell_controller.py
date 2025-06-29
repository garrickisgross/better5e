from models.spell import Spell
from repos.spell import Spell

class SpellController:
    @staticmethod
    def create_spell(spell_data: dict) -> int:
        spell = Spell(**spell_data)
        return Spell.create(spell)

    @staticmethod
    def get_spell(spell_id: int) -> Spell:
        return Spell.get(spell_id)

    @staticmethod
    def list_spells() -> list[Spell]:
        return Spell.list_all()

    @staticmethod
    def update_spell(spell_id: int, updates: dict) -> None:
        Spell.update(spell_id, updates)

    @staticmethod
    def delete_spell(spell_id: int) -> None:
        Spell.delete(spell_id)