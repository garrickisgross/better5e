import sys
from uuid import UUID, uuid4
import pytest
from datetime import datetime
from pydantic import ValidationError

# --- Setup dummy engine modules for Character tests ---
class DummyRulesEngine:
    def compute(self, state):
        return {'computed': True}
    def apply_event(self, state, event):
        state.event_applied = event

class DummyState:
    def __init__(self):
        self.asset_ids = []
        self._mod_cache = ['initial']
        self.event_applied = None

# Inject dummy modules before importing Character
sys.modules['engine.rules_engine'] = type(sys)('engine.rules_engine')
setattr(sys.modules['engine.rules_engine'], 'RulesEngine', DummyRulesEngine)
sys.modules['engine.state'] = type(sys)('engine.state')
setattr(sys.modules['engine.state'], 'CharacterState', DummyState)

# Now import modules under test
import models.primitives as primitives # file: primitives.py
import models.types as types_module # file: types.py
import models.character as character  # file: character.py

# --- Tests for primitives.py ---

def test_stat_valid_and_defaults():
    s = primitives.Stat(key='STR', name='Strength', description='desc', default=True)
    assert isinstance(s.id, UUID)
    assert s.key == 'STR'
    assert s.name == 'Strength'
    assert s.description == 'desc'
    assert s.default is True

@pytest.mark.parametrize('invalid_key', ['AB', 'STRG', 'str', '123', 'A B'])
def test_stat_invalid_key(invalid_key):
    with pytest.raises(ValidationError):
        primitives.Stat(key=invalid_key, name='Name')


def test_skill_validate_gov_stat():
    skill = primitives.Skill(key='PERSU', name='Persuasion', governing_stat_key='CHA', default=False)
    # valid governing_stat_key
    stats = {'CHA': primitives.Stat(key='CHA', name='Charisma')}
    # should not raise
    primitives.Skill.validate_gov_stat(skill, stats)

    # invalid governing_stat_key
    skill_bad = primitives.Skill(key='ATHLT', name='Athletics', governing_stat_key='BER', default=False)
    with pytest.raises(ValueError):
        primitives.Skill.validate_gov_stat(skill_bad, {})


def test_modifier_validate_key():
    m = primitives.Modifier(target_key='STR', op='add', value=5)
    stats = {'STR': primitives.Stat(key='STR', name='Strength')}
    skills = {'STRNG': primitives.Skill(key='STRNG', name='Strange', governing_stat_key='STR', default=True)}
    # valid case
    m.validate_key(stats, skills)

    # invalid case: missing key
    m_bad = primitives.Modifier(target_key='DEX', op='set', value=2)
    with pytest.raises(ValueError):
        m_bad.validate_key({}, {})


def test_asset_defaults():
    a = primitives.Asset(type='stat', name='TestAsset', created_by='Tester')
    assert isinstance(a.id, UUID)
    assert a.type == 'stat'
    assert a.name == 'TestAsset'
    assert a.text == ''
    assert a.tags == []
    assert a.data is None
    assert isinstance(a.created_at, datetime)


def test_feature_data_list_independence():
    fd1 = primitives.FeatureData()
    fd2 = primitives.FeatureData()
    assert fd1.action_cost is None
    assert fd1.modifiers == []
    assert fd1.grants == []
    # mutate one, other should not change
    fd1.modifiers.append(primitives.Modifier(target_key='STR', op='add', value=1))
    assert fd2.modifiers == []


def test_empty_data_classes():
    for cls in (primitives.SpellData, primitives.ItemData, primitives.ClassData, primitives.SubClassData, primitives.ResourceData):
        inst = cls()
        # BaseModel with no fields yields empty dict
        assert inst.dict() == {}

# --- Tests for types.py ---

def test_asset_subclasses_have_correct_type_and_data():
    data = primitives.FeatureData()
    feat = types_module.Feature(name='Feat', created_by='User', data=data)
    assert feat.type == 'feature'
    assert isinstance(feat.data, primitives.FeatureData)

    spell = types_module.Spell(name='Spell', created_by='User', data=primitives.SpellData())
    assert spell.type == 'spell'

    item = types_module.Item(name='Item', created_by='User', data=primitives.ItemData())
    assert item.type == 'item'

    cls = types_module.Class(name='Class', created_by='User', data=primitives.ClassData())
    assert cls.type == 'class'

    sub = types_module.Subclass(name='SubClass', created_by='User', data=primitives.SubClassData())
    assert sub.type == 'subclass'

    res = types_module.Resource(name='Resource', created_by='User', data=primitives.ResourceData())
    assert res.type == 'resource'

# --- Tests for character.py ---

def test_character_totals_and_events_and_add_asset():
    state = DummyState()
    rules = DummyRulesEngine()
    char = character.Character(state, rules)

    # totals property uses compute()
    result = char.totals
    assert result == {'computed': True}

    # long_rest applies event and clears cache
    state._mod_cache.append('dirty')
    char.long_rest()
    assert state._mod_cache == []
    assert state.event_applied == 'long_rest'

    # add_asset appends and clears cache
    new_id = uuid4()
    state._mod_cache.append('dirty')
    char.add_asset(new_id)
    assert new_id in state.asset_ids
    assert state._mod_cache == []
