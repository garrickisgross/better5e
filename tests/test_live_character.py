from better5e.character import Character
from better5e.game_objects import Feature, Race
from better5e.modifiers import Modifier, ModifierOperation
from better5e.live_character import LiveCharacter


class DummyDAO:
    def __init__(self, objects):
        self.objects = {obj.uuid: obj for obj in objects}

    def load(self, obj_id):
        return self.objects[obj_id]


def test_live_character_initialization_and_grants():
    granted = Feature(
        name="Granted",
        modifiers=[
            Modifier(target="stats.strength", operation=ModifierOperation.ADD, value=1)
        ],
    )
    race = Race(name="Race", grants=[granted.uuid])
    base_feat = Feature(
        name="Base",
        modifiers=[
            Modifier(target="stats.strength", operation=ModifierOperation.ADD, value=2)
        ],
    )
    dao = DummyDAO([granted])
    char = Character(name="Hero", race=race, features=[base_feat])
    live = LiveCharacter(char, dao)
    # granted feature should be present
    assert any(f.uuid == granted.uuid for f in live.features)
    # total strength: 10 base +2 from base_feat +1 from granted
    assert live.get_stat("strength") == 13


def test_live_character_grant_and_set_data():
    feat = Feature(
        name="DexFeat",
        modifiers=[
            Modifier(target="stats.dexterity", operation=ModifierOperation.ADD, value=1)
        ],
    )
    dao = DummyDAO([feat])
    live = LiveCharacter(Character(name="Hero"), dao)
    live.grant(feat.uuid)
    assert live.get_stat("dexterity") == 11
    live.set_data("stats.dexterity", 14)
    assert live.get_stat("dexterity") == 15
    data = live.to_dict()
    assert data["stats"]["dexterity"] == 14
    assert "dao" not in data


def test_live_character_prevents_duplicate_grants_and_handles_cycles():
    feat_a = Feature(name="A")
    feat_b = Feature(name="B", grants=[feat_a.uuid])
    feat_a.grants.append(feat_b.uuid)
    dao = DummyDAO([feat_a, feat_b])
    live = LiveCharacter(Character(name="Hero"), dao)
    live.grant(feat_a.uuid)
    live.grant(feat_a.uuid)
    ids = [f.uuid for f in live.features]
    assert ids.count(feat_a.uuid) == 1
    assert ids.count(feat_b.uuid) == 1
    live.set_data("name", "Warrior")
    assert live.name == "Warrior"
    assert f"set:name" in live.events
    assert live.get_modifier("strength") == 0


def test_live_character_get_stat_branches():
    grant_mod = Modifier(target="stats.strength", operation=ModifierOperation.GRANT, value="x")
    other_mod = Modifier(target="stats.dexterity", operation=ModifierOperation.ADD, value=1)
    feat = Feature(name="Feat", modifiers=[grant_mod, other_mod])
    live = LiveCharacter(Character(name="Hero", features=[feat]), DummyDAO([]))
    assert live.get_stat("strength") == 10
    assert live.get_stat("constitution") == 10
