from uuid import UUID

from rich.console import Console
from rich.prompt import Prompt, IntPrompt

from schema.feature import Feature
from schema.class_ import Class
from schema.subclass import Subclass
from schema.spellcasting import Spellcasting
from schema.spell import Spell
from schema.item import Item
from schema.character import Character
from schema.primitives import Modifier

console = Console()


def create_feature() -> Feature:
    description = Prompt.ask("Feature description")
    modifiers: list[Modifier] = []
    count = IntPrompt.ask("Number of modifiers", default=0)
    for i in range(count):
        console.print(f"Modifier {i + 1}")
        target = Prompt.ask("Target")
        op = Prompt.ask("Operation", choices=["add", "set", "grant"])
        value_raw = Prompt.ask("Value")
        try:
            value: int | UUID = int(value_raw)
        except ValueError:
            value = UUID(value_raw)
        modifiers.append(Modifier(target=target, op=op, value=value))
    feat = Feature(description=description, modifiers=modifiers)
    console.print(feat.model_dump())
    return feat


def create_class() -> Class:
    hit_die = IntPrompt.ask("Hit die")
    features: dict[int, list[UUID]] = {}
    subclasses: list[UUID] = []
    cls = Class(hit_die=hit_die, features=features, subclasses=subclasses)
    console.print(cls.model_dump())
    return cls


def create_subclass() -> Subclass:
    parent_id = UUID(Prompt.ask("Parent class UUID"))
    features: dict[int, list[UUID]] = {}
    sub = Subclass(parent=parent_id, features=features)
    console.print(sub.model_dump())
    return sub


def create_spellcasting() -> Spellcasting:
    ability = Prompt.ask("Spellcasting ability")
    spell_list: list[UUID] = []
    slots: dict[int, dict[int, int]] = {}
    sc = Spellcasting(ability=ability, spell_list=spell_list, slots=slots)
    console.print(sc.model_dump())
    return sc


def create_spell() -> Spell:
    level = IntPrompt.ask("Spell level")
    school = Prompt.ask("School")
    casting_time = Prompt.ask("Casting time")
    range_ = Prompt.ask("Range")
    components = Prompt.ask("Components (comma separated)").split(",")
    components = [c.strip() for c in components if c.strip()]
    duration = Prompt.ask("Duration")
    description = Prompt.ask("Description")
    spell = Spell(
        level=level,
        school=school,
        casting_time=casting_time,
        range=range_,
        components=components,
        duration=duration,
        description=description,
    )
    console.print(spell.model_dump())
    return spell


def create_item() -> Item:
    category = Prompt.ask("Category", choices=["weapon", "consumable", "armor"])
    equipped = Prompt.ask("Equipped?", choices=["y", "n"], default="n") == "y"
    modifiers: list[Modifier] = []
    count = IntPrompt.ask("Number of modifiers", default=0)
    for i in range(count):
        console.print(f"Modifier {i + 1}")
        target = Prompt.ask("Target")
        op = Prompt.ask("Operation", choices=["add", "set", "grant"])
        value_raw = Prompt.ask("Value")
        try:
            value: int | UUID = int(value_raw)
        except ValueError:
            value = UUID(value_raw)
        modifiers.append(Modifier(target=target, op=op, value=value))
    item = Item(category=category, equipped=equipped, modifiers=modifiers)
    console.print(item.model_dump())
    return item


def create_character() -> Character:
    ac = IntPrompt.ask("Armor Class")
    pb = IntPrompt.ask("Proficiency bonus")
    background = UUID(Prompt.ask("Background UUID"))
    race = UUID(Prompt.ask("Race UUID"))
    char = Character(
        ac=ac,
        ability_scores={},
        proficiency_bonus=pb,
        skills={},
        background=background,
        race=race,
        features=[],
        inventory=[],
        classes=[],
    )
    console.print(char.model_dump())
    return char


def main() -> None:
    console.print("[bold underline]Better5e CLI[/]")
    actions = {
        "feature": create_feature,
        "class": create_class,
        "subclass": create_subclass,
        "spellcasting": create_spellcasting,
        "spell": create_spell,
        "item": create_item,
        "character": create_character,
    }
    while True:
        choice = Prompt.ask(
            "Create which object?", choices=list(actions.keys()) + ["quit"], default="quit"
        )
        if choice == "quit":
            break
        action = actions[choice]
        action()


if __name__ == "__main__":
    main()
