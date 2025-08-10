from better5e.models.game_object import Feature
from better5e.engine.wizard import BuildWizard

ws = BuildWizard()

session = ws.start(Feature)
spec = ws.current_step(session)

for i in spec.fields:
    print(i)
    