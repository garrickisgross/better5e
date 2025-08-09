from better5e.game_objects import GameObj, Resource, Action, Rollable, Grant, Modifier
from better5e.dao import SQLite3DAO

actions = [Action(type="action", roll=Rollable(num=2, sides=8))]
resources = [ Resource(uses_max=4, uses_current=0, actions=actions) for _ in range(2)]

obj = GameObj(name="test", kind="feature", desc="test object", modifiers=None, grants=None, resources=resources)

dao = SQLite3DAO()

dao.save(obj)

print("saved")

uuid = obj.id

copy = dao.load_by_id(uuid)

list_of_objs = dao.load_by_kind("feature")

assert copy == obj

print(list_of_objs)