from typing import List, Any
from models.item import Item, Weapon, Armor, Consumable, Tool
from repos.item import ItemRepo, WeaponRepo, ArmorRepo, ConsumableRepo, ToolRepo

class ItemController:
    
    @staticmethod
    def create_item(item_data: dict) -> int:
        item = Item(**item_data)
        return ItemRepo.create(item)

    @staticmethod
    def get_item(item_id: int) -> Item:
        return ItemRepo.get(item_id)

    @staticmethod
    def list_items() -> List[Item]:
        return ItemRepo.list_all()

    @staticmethod
    def update_item(item_id: int, updates: dict) -> None:
        ItemRepo.update(item_id, updates)

    @staticmethod
    def delete_item(item_id: int) -> None:
        ItemRepo.delete(item_id)

class WeaponController:
    
    @staticmethod
    def create_weapon(weapon_data: dict) -> int:
        weapon = Weapon(**weapon_data)
        return WeaponRepo.create(weapon)

    @staticmethod
    def get_weapon(weapon_id: int) -> Weapon:
        return WeaponRepo.get(weapon_id)

    @staticmethod
    def list_weapons() -> List[Weapon]:
        return WeaponRepo.list_all()

    @staticmethod
    def update_weapon(weapon_id: int, updates: dict) -> None:
        WeaponRepo.update(weapon_id, updates)

    @staticmethod
    def delete_weapon(weapon_id: int) -> None:
        WeaponRepo.delete(weapon_id)

class ArmorController:
    
    @staticmethod
    def create_armor(armor_data: dict) -> int:
        armor = Armor(**armor_data)
        return ArmorRepo.create(armor)

    @staticmethod
    def get_armor(armor_id: int) -> Armor:
        return ArmorRepo.get(armor_id)

    @staticmethod
    def list_armors() -> List[Armor]:
        return ArmorRepo.list_all()

    @staticmethod
    def update_armor(armor_id: int, updates: dict) -> None:
        ArmorRepo.update(armor_id, updates)

    @staticmethod
    def delete_armor(armor_id: int) -> None:
        ArmorRepo.delete(armor_id)

class ConsumableController:
    
    @staticmethod
    def create_consumable(consumable_data: dict) -> int:
        consumable = Consumable(**consumable_data)
        return ConsumableRepo.create(consumable)

    @staticmethod
    def get_consumable(consumable_id: int) -> Consumable:
        return ConsumableRepo.get(consumable_id)

    @staticmethod
    def list_consumables() -> List[Consumable]:
        return ConsumableRepo.list_all()

    @staticmethod
    def update_consumable(consumable_id: int, updates: dict) -> None:
        ConsumableRepo.update(consumable_id, updates)

    @staticmethod
    def delete_consumable(consumable_id: int) -> None:
        ConsumableRepo.delete(consumable_id)

class ToolController:
    
    @staticmethod
    def create_tool(tool_data: dict) -> int:
        tool = Tool(**tool_data)
        return ToolRepo.create(tool)

    @staticmethod
    def get_tool(tool_id: int) -> Tool:
        return ToolRepo.get(tool_id)

    @staticmethod
    def list_tools() -> List[Tool]:
        return ToolRepo.list_all()

    @staticmethod
    def update_tool(tool_id: int, updates: dict) -> None:
        ToolRepo.update(tool_id, updates)

    @staticmethod
    def delete_tool(tool_id: int) -> None:
        ToolRepo.delete(tool_id)