from better5e.dao.sqlite import DAO
from better5e.models.game_object import AnyGameObj
from pydantic import TypeAdapter 

db  = DAO()


feats = """[
  {
    "id": "e1a9b7a8-0c1d-4d64-9b8b-2d9f4ad7a9b0",
    "kind": "feature",
    "name": "Darkvision",
    "desc": "You can see in dim light within 60 feet as if it were bright light.",
    "actions": [],
    "modifiers": [
      { "target": "senses.darkvision", "op": "set", "value": 60 }
    ],
    "grants": [],
    "uses_max": null,
    "recharge": null
  },
  {
    "id": "2a5b2762-2d2b-4b35-94ed-3b6c5d6a9c71",
    "kind": "feature",
    "name": "Second Wind",
    "desc": "On your turn, regain hit points as a bonus action.",
    "actions": [],
    "modifiers": [],
    "grants": [],
    "uses_max": 1,
    "recharge": "short_rest"
  },
  {
    "id": "7f3b7e7a-4e05-4f07-9b6a-0d3a9d3a2f44",
    "kind": "feature",
    "name": "Fighting Style: Defense",
    "desc": "While wearing armor, you gain a +1 bonus to AC.",
    "actions": [],
    "modifiers": [
      { "target": "defense.ac", "op": "add", "value": 1 }
    ],
    "grants": [],
    "uses_max": null,
    "recharge": null
  },
  {
    "id": "b6f4b3a2-0b9c-4ad9-9f3e-0d7b2a4c5e88",
    "kind": "feature",
    "name": "Lucky",
    "desc": "You have 3 luck points to reroll d20s.",
    "actions": [],
    "modifiers": [],
    "grants": [],
    "uses_max": 3,
    "recharge": "long_rest"
  },
  {
    "id": "0c9a7d3f-1c2b-4f5a-93e7-2a1b4c6d8e90",
    "kind": "feature",
    "name": "Stone's Endurance",
    "desc": "Use your reaction to reduce damage you take.",
    "actions": [],
    "modifiers": [],
    "grants": [],
    "uses_max": 1,
    "recharge": "short_rest"
  }
]"""

TA_LIST = TypeAdapter(list[AnyGameObj])

objects: list[AnyGameObj] = TA_LIST.validate_json(feats)

for obj in objects:
    db.save(obj)

