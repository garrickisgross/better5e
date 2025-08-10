from dataclasses import dataclass, field
from typing import Any
from pydantic import BaseModel, ValidationError
from pydantic.fields import FieldInfo

@dataclass
class FieldSpec:
    name: str
    schema: dict[str, Any]  # the JSON Schema fragment for the field
    required: bool
    ui: dict[str, Any] = field(default_factory=dict)

@dataclass
class StepSpec:
    title: str
    fields: list[FieldSpec]
    order: int = 0

def build_step_plan(json_schema: dict[str, Any]) -> list[StepSpec]:
    props = json_schema.get("properties", {})
    required = set(json_schema.get("required", []))
    groups: dict[str, StepSpec] = {}

    def extract_ui(node: dict[str, Any]) -> dict[str, Any]:
        # Your hints live here; keep key names namespaced to avoid collisions
        return node.get("json_schema_extra", {}) or {}

    for name, node in props.items():
        # resolve $ref once for display metadata (simple resolver)
        if "$ref" in node:
            ref = node["$ref"].split("/")[-1]
            node = json_schema.get("$defs", {}).get(ref, node)

        ui = extract_ui(node)
        group_name = ui.get("ui:group", "General")
        groups.setdefault(group_name, StepSpec(title=group_name, fields=[], order=ui.get("ui:groupOrder", 0)))

        groups[group_name].fields.append(
            FieldSpec(
                name=name,
                schema=node,
                required=name in required,
                ui=ui
            )
        )

    # per-step field ordering (ui:order), else alphabetical
    for step in groups.values():
        step.fields.sort(key=lambda f: (f.ui.get("ui:order", 1_000_000), f.name))

    # step ordering (ui:groupOrder), else by title
    steps = sorted(groups.values(), key=lambda s: (s.order, s.title))
    return steps

def make_step_model(parent: type[BaseModel], field_names: list[str]) -> type[BaseModel]:
    fields = {}
    for name in field_names:
        f = parent.model_fields[name]  # v2
        ann = f.annotation
        # Reuse metadata; if no default use Ellipsis to mark "required"
        default: FieldInfo | object = f.default if f.default is not None else ...
        # Preserve description/constraints/etc. by providing a Field(...) again
        if isinstance(default, FieldInfo):
            fields[name] = (ann, default)
        else:
            # reconstruct Field with same extras (minimal; adjust as needed)
            fields[name] = (ann, f.field_info)
    StepModel = create_model(f"{parent.__name__}Step", __base__=BaseModel, **fields)  # type: ignore
    return StepModel

def validate_step(parent: type[BaseModel], step_fields: list[str], step_data: dict):
    StepModel = make_step_model(parent, step_fields)
    return StepModel.model_validate(step_data)  # raises ValidationError on bad input    

@dataclass
class WizardSession:
    model_cls: type[BaseModel]
    steps: list[StepSpec]
    current: int = 0
    data: dict[str, Any] = field(default_factory=dict)

class BuildWizard:
    def start(self, model_cls: type[BaseModel]) -> WizardSession:
        schema = model_cls.model_json_schema()
        steps = build_step_plan(schema)
        return WizardSession(model_cls=model_cls, steps=steps)
    
    def current_step(self, ws: WizardSession) -> StepSpec:
        return ws.steps[ws.current]
    
    def apply(self, ws: WizardSession, payload: dict[str, Any]) -> dict[str, Any] | None:
        step = self.current_step(ws)
        names = [f.name for f in step.fields]
        try:
            # Validate the fields for this step
            validate_step(ws.model_cls, names, {k:v for k,v in payload.items() if k in names})
        except ValidationError as e:
            return e.errors()
        
        #merge into session data
        ws.data.update({k:v for k, v in payload.items() if k in names})
        ws.current += 1
        return None

    def can_finish(self, ws: WizardSession) -> bool:
        return ws.current >= len(ws.steps)
    
    def finish(self, ws: WizardSession) -> BaseModel:
        return ws.model_cls.model_validate(ws.data)
    