# Designing a Django-Based D\&D 5E Character Model for Maximum Customization

## Introduction and Goals

Building a robust Dungeons & Dragons 5th Edition (5e) character model in Django requires carefully structuring data to cover all aspects of a character (classes, subclasses, species/races, subraces, backgrounds, feats/features, items, spells, etc.) while allowing extensive homebrew customization. The goal is to loosely follow official 5e SRD standards under the Open Gaming License (OGL) as a baseline, but with far more flexibility than a platform like D\&D Beyond (which supports homebrew but with limitations) \[1]. This means users can create their own content at every turn – defining new classes, races, features, and so on – and have those integrate seamlessly into character creation.

To achieve this, we will design a normalized relational schema (with some JSON hybridization where appropriate) that avoids redundancy and uses join tables for complex many-to-many relations \[2]. Each major game concept (ability scores, skills, classes, races, backgrounds, items, etc.) will be represented by its own Django model/table \[2]. This separation not only mirrors the structure of D\&D 5e rules, but also makes the data easier to extend. In addition, we’ll incorporate JSON fields for highly variable or nested data (like lists of proficiency options or dynamic feature data) to keep the schema flexible. Ultimately, the design focuses on the end user experience: a web UI where users can intuitively build characters and homebrew content without being constrained by a rigid system.

## Core Character Model Overview

At the heart is the `Character` model, which ties together all the components of a character. This model will include core identity fields and foreign keys to the character’s chosen options: e.g., name, player (`User`), species (race), subrace (if any), background, etc. It will also track primary stats like ability scores and other sheet-specific info. Key design points include:

* **Ability Scores:** Six fields on `Character` for Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma (or a related model). These are fundamental to every character \[3]. Alternatively, a separate `AbilityScore` model (with records for STR, DEX, etc.) and a join table for a character’s scores could be used, but simple integer fields are straightforward since 5e has a fixed set of scores.
* **Proficiency Bonus:** Can be derived from total level, but we might store it or compute on the fly. Skills and saves use this bonus if proficient.
* **Skills:** Define a `Skill` model (e.g., Stealth, Arcana) each linked to an ability score (e.g., Stealth → Dexterity) \[3]. Characters have a many-to-many relationship with `Skill` to indicate proficiency/expertise. For example, a join table `CharacterSkill` could store character, skill, and a level of proficiency (normal or expert).
* **Saving Throws:** Saving throw proficiencies can be represented either as boolean fields on `Character` (e.g., `prof_str_save`) or as entries in the Proficiency model. Since classes grant specific saving throw proficiencies, we will capture that in the `Class` model and apply it to `Character` (see Class section).
* **Other Character Info:** Fields like alignment, age, gender, deity, etc. can be simple `CharField`/`TextField`. HP and hit dice can be calculated from class and level, but current/temporary HP may be stored if the app will track them. Likewise, fields for inspiration, XP, and coin inventory can be added.

The `Character` model will mostly reference other models rather than storing large JSON blobs to keep data relational and ensure integrity (e.g., `character.species` is a `ForeignKey` to a `Species` model). However, we may include a `JSONField` on `Character` to store miscellaneous custom attributes or choices that don’t warrant dedicated columns.

## Species (Race) and Origins

**Species** represents the character’s race or lineage (e.g., Human, Elf, Dwarf). Use a `Species` model with fields capturing SRD-style racial traits but designed for extensibility \[4]\[5]:

* `name` – e.g., “Elf.”
* `speed` – base walking speed in feet \[4].
* **Ability Score Bonuses** – Model via one-to-many `SpeciesAbilityBonus` (fields: species, ability, bonus) or as JSON mapping. Relational is clearer and queryable, and handles user-defined values well \[6].
* `size` – category (Small, Medium) and possibly a `size_description` \[7]\[8].
* `alignment` and `age` – flavor text per SRD \[5]\[9].
* **Proficiencies & Languages** – Handle with relations to a `Proficiency` model and a `Language` model:

  * `starting_proficiencies` – M2M to `Proficiency` for automatic proficiencies \[10]\[11].
  * `proficiency_choices` – JSON/related table representing choice groups (e.g., choose 1 tool from a list) \[12]\[13].
  * `languages` – M2M to `Language` \[11] plus optional language choice JSON; `language_desc` for flavor \[14].
* **Traits** – Many racial abilities model well as distinct `Trait` objects (e.g., Darkvision, Fey Ancestry), with M2M from `Species` \[15].
* **Subraces** – `Subrace` model linked to parent `Species` (one-to-many) for additional traits/bonuses \[16].

**Origins:** To maximize customization, optionally support an `Origin` (heritage/culture) system separate from species, granting bonuses or proficiencies, mixable with any species. Backgrounds can cover some of this, but an `Origin` model adds flexibility.

## Classes and Subclasses

Model base classes with a `Class` model and archetypes with a `Subclass` model. Key `Class` fields/relations:

* `name` – e.g., “Barbarian.”
* `hit_die` – e.g., 12 for Barbarian (d12 per level) \[17]\[18].
* **Primary/Spellcasting Ability:** Optional FK to `AbilityScore`; add `spellcasting_ability` where applicable \[25]\[26].
* **Saving Throws:** M2M to `AbilityScore` for the two saves \[19].
* **Starting Proficiencies:** M2M to `Proficiency` for automatic proficiencies; `proficiency_choices` as JSON for “choose N of these skills/tools…” \[20]\[21].
* **Starting Equipment:** Guaranteed gear via M2M to `Item` (with quantity through model) and `starting_equipment_options` as JSON for choice packs \[22]\[23]\[24].
* **Spellcasting:** Optional details (e.g., spell slots/known progression) either hardcoded, in JSON, or separate model \[25]\[26].
* **Multiclassing Prerequisites:** JSON/related records with ability minimums \[27]\[28].
* **Class Features:** One-to-many relation to `ClassFeature` with `level_acquired` \[29].

`Subclass` links to the parent `Class` with its own description, optional bonus spells (M2M to `Spell`), and one-to-many `SubclassFeature` \[30]\[31]\[32]. The `Class` model has one-to-many `Subclass` \[33].

> **Design note:** For features, you can keep separate `ClassFeature`/`SubclassFeature` models or unify with a single `Feature` model (nullable `class`/`subclass` fields) mirroring SRD API structure \[35]\[36].

## Features and Feats

* **ClassFeature:** `name`, `description`, `class` FK, `level_acquired`, optional `feature_type`/tags and `parent_feature` for option groups (e.g., Fighting Style) \[34]\[41]\[42].
* **SubclassFeature:** same, with `subclass` FK.
* **Trait:** Racial traits; `name`, `description`, optional mechanical JSON (e.g., `{ "darkvision_range": 60 }`).
* **Feat:** `name`, `description`, optional structured prerequisites and granted effects; can relate to `Proficiency` and/or encode small effects in JSON. Keep simple initially.

Background features can live directly on the `Background` model or in a small `BackgroundFeature` model.

## Backgrounds

`Background` represents characters’ backgrounds (e.g., Acolyte, Soldier):

* `name`, `description`.
* `feature_name`, `feature_desc` – narrative feature.
* **Proficiencies:**

  * `skill_proficiencies` – M2M to `Skill` (usually two) \[43].
  * `tool_proficiencies` – M2M to `Proficiency`.
  * `tool_choices` / `language_choices` – JSON for optional choice logic.
  * `languages` – M2M to `Language`.
* **Equipment/Gold:** simple text or structured relations as needed.
* **Personality tables:** optional JSON (purely flavor).

Optionally allow ability score bonuses (e.g., One D\&D style) or use `Origin` for that.

## Items and Equipment

Create a general `Item` model covering weapons, armor, gear, consumables, magic items:

* `name`, `category`, `weight`, `cost` (e.g., store in copper), `description`.
* **Type-specific Data:** store in a flexible `JSONField`:

  * Weapons: `{"weapon": {"damage": "1d8", "damage_type": "slashing", "properties": ["Versatile 1d10", "Finesse"], "range_normal": 20, "range_long": 60}}`
  * Armor: `{"armor": {"ac": 15, "stealth_disadvantage": true, "strength_requirement": 13}}`
  * Magic effects: arbitrary JSON.
* **Proficiency linkage:** optional FK to `Proficiency` category (e.g., “Martial Weapons”).
* **Inventory:** `CharacterItem` through model: `character`, `item`, `quantity`, `equipped` (and optional slot/location).

This JSON-backed polymorphism avoids dozens of nullable columns and supports homebrew flexibility \[37].

## Spells and Spellcasting

* **Spell** model: `name`, `level` (0–9), `school`, `casting_time`, `range`, `components` (V/S/M flags plus materials), `duration`, `description`, optional attack/save, damage/effect typing, etc.
* **Class Spell Lists:** M2M `Class` ↔ `Spell`; optional `Subclass` bonus spells M2M \[31]\[32].
* **Character spells:** Optional M2M/through model (`CharacterSpell`) to track known/prepared spells; for simplicity, store known spells and manage prep in UI. Multiclass granularity can be added later.

Seed with SRD/Open5e content for immediate usability \[38]\[44].

## Modeling Multiclass Characters

Use a join model `CharacterClass` to link a `Character` to each `Class` (and chosen `Subclass`) with a `level`. Sum related levels to compute total level:

* `CharacterClass`: `character` FK, `class` FK, `subclass` (nullable) FK, `level`, optional `class_order`/`is_primary`.

Feature/proficiency aggregation:

* **Class/Subclass Features:** query `ClassFeature`/`SubclassFeature` where `level_acquired ≤ character’s level in that class` \[34].
* **Racial Traits:** from `Species`/`Subrace`.
* **Feats/Background:** from character’s M2M and background fields.

## Utilizing JSON Fields (Hybrid Approach)

Django’s `JSONField` helps with structured yet variable data \[39]:

* **Choice structures** (e.g., “choose N of these skills/tools/equipment”) \[20]\[23].
* **Item polymorphism** (weapon/armor/etc.) \[37].
* **Optional effects** on `Feat`/`Feature` (simple, structured boosts).
* **Variant/optional features** and future-proofing.

Trade-off: JSON can’t enforce FK integrity; mitigate via validation helpers and consistent keys (names or PKs).

## Connected Data and Relationships Diagram

Below is a simplified outline of main models and relations (pseudo-model syntax):

```text
AbilityScore  (name, abbreviation)
Skill         (name, ability -> AbilityScore)
Proficiency   (name, category/type)
Language      (name)

Species       (name, speed, size, alignment_desc, age_desc, size_desc, ...)
  ├─ M2M -> Trait
  ├─ M2M -> Proficiency (starting_proficiencies)
  ├─ JSON starting_proficiency_options
  ├─ M2M -> Language
  ├─ JSON language_choices
  └─ 1..* SpeciesAbilityBonus (species, ability -> AbilityScore, bonus)
Subrace       (name, parent_species -> Species, ...)
Trait         (name, description, [json_mechanics])

Class         (name, hit_die, spellcasting_ability? -> AbilityScore, ...)
  ├─ M2M -> AbilityScore (saving_throws)
  ├─ M2M -> Proficiency (proficiencies)
  ├─ JSON proficiency_choices
  ├─ M2M -> Spell (spell_list)
  ├─ 1..* ClassFeature
  └─ 1..* Subclass
Subclass      (name, class -> Class, subclass_flavor, ...)
  ├─ M2M -> Spell (bonus spells) [optional]
  └─ 1..* SubclassFeature
ClassFeature  (name, description, class -> Class, level_acquired, parent_feature?)
SubclassFeature (name, description, subclass -> Subclass, level_acquired, parent_feature?)
Feat          (name, description, [prereqs JSON], [granted proficiencies], [ability bonuses])

Background    (name, description, feature_name, feature_desc, ...)
  ├─ M2M -> Skill (skill_proficiencies)
  ├─ M2M -> Proficiency (tool_proficiencies)
  ├─ JSON tool_choices / language_choices
  └─ M2M -> Language (languages)

Item          (name, category, weight, cost, description, json_details)
CharacterItem (character -> Character, item -> Item, quantity, equipped)

Spell         (name, level, school, casting_time, range, components, duration, description, ...)

Character     (user -> User, name, species -> Species, subrace? -> Subrace,
               origin? -> Origin, background -> Background, STR/DEX/CON/INT/WIS/CHA,
               alignment, xp, etc.)
  ├─ 1..* CharacterClass (class -> Class, subclass? -> Subclass, level, is_primary?)
  ├─ M2M -> Feat (feats) [through CharacterFeat if tracking level gained]
  ├─ [M2M -> Skill or Proficiency as final proficiencies (optional cache)]
  ├─ M2M -> Language (final languages)
  ├─ 1..* CharacterItem (inventory)
  └─ M2M -> Spell (known/prepared) [optional through CharacterSpell]
```

This mirrors SRD data organization (classes, races, features, etc.) and keeps the system normalized and extensible \[2]\[18]\[4].

## Admin and UI Considerations for Customization

* **Django Admin:** Inline forms (e.g., add `ClassFeature` inline under `Class`). Power users can seed SRD fixtures.
* **Custom Forms/Views:** Multi-step “builder” flows for creating classes/races with feature/proficiency choices.
* **Validation:** Model/form `clean()` to validate JSON shape, resolve names to actual records, etc.
* **Seed OGL/CC Content:** Preload SRD subsets from Open5e/5e API; mark as official (`is_official`) and support `created_by` for user homebrew \[44].
* **Content Scoping:** Separate official vs homebrew in UI; per-user visibility/publishing as needed.
* **Character Creation Flow:**

  1. Species/Subrace/Origin → apply traits/proficiencies;
  2. Class → prompt skill/tool choices (from JSON) and features by level;
  3. Subclass at the right level;
  4. Background → grant fixed proficiencies + optional language/tool choices;
  5. Feats (if variant/level supports);
  6. Starting equipment (parse JSON choice packs) or “shop”;
  7. Spells (from class spell list) as needed.

The data-driven approach ensures custom content “just works” through universal flows.

## Conclusion

The proposed Django schema balances normalization and flexibility. Core entities (attributes, skills, classes, races, backgrounds, items, spells) are cleanly separated and related, while JSON fields capture complex choice structures and polymorphic item/spell specifics. The design follows 5e SRD structure (e.g., class hit die, saving throws, proficiencies, subclasses) \[18]\[19], race traits/bonuses/speed/size \[4]\[40], and feature linking by level \[34]\[35], while enabling richer customization than standard tools. With fixtures seeded from OGL/CC sources and friendly builder UIs, users can create original content (species, classes, features, items, spells) and immediately build characters with it—yielding a powerful, extensible 5e character platform.

## Sources

1. *Is there a DnDbeyond alternative that allows for custom class …* (Reddit) — [https://www.reddit.com/r/DnD/comments/12bzzjw/is\_there\_a\_dndbeyond\_alternative\_that\_allows\_for/](https://www.reddit.com/r/DnD/comments/12bzzjw/is_there_a_dndbeyond_alternative_that_allows_for/)
   2,3,29,43. Paula Marrero, **Building a D\&D 5e Character Generator: A Journey Through SQL and RPG Complexity** (DEV) — [https://dev.to/paulama3/building-a-dd-5e-character-generator-a-journey-through-sql-and-rpg-complexity-4pb7](https://dev.to/paulama3/building-a-dd-5e-character-generator-a-journey-through-sql-and-rpg-complexity-4pb7)
   4–16,40. **5e SRD API – Get a race by index** — [https://5e-bits.github.io/docs/api/get-a-race-by-index](https://5e-bits.github.io/docs/api/get-a-race-by-index)
2. **Barbarian | D\&D 5e Wiki (Fandom)** — [https://dnd-5e.fandom.com/wiki/Barbarian](https://dnd-5e.fandom.com/wiki/Barbarian)
   18–28,33. **5e SRD API – Get a class by index** — [https://5e-bits.github.io/docs/api/get-a-class-by-index](https://5e-bits.github.io/docs/api/get-a-class-by-index)
   30–32. **5e SRD API – Get a subclass by index** — [https://5e-bits.github.io/docs/api/get-a-subclass-by-index](https://5e-bits.github.io/docs/api/get-a-subclass-by-index)
   34–36,41–42. **5e SRD API – Get a feature by index** — [https://5e-bits.github.io/docs/api/get-a-feature-by-index](https://5e-bits.github.io/docs/api/get-a-feature-by-index)
3. Neelik, **django-dnd** (GitHub) — [https://github.com/Neelik/django-dnd](https://github.com/Neelik/django-dnd)
4. **D\&D 5e API (WireMock catalog)** — [https://library.wiremock.org/catalog/api/d/dnd5eapi.co/dnd5eapi-co/](https://library.wiremock.org/catalog/api/d/dnd5eapi.co/dnd5eapi-co/)
5. **Django Model field reference – JSONField** — [https://docs.djangoproject.com/en/5.2/ref/models/fields/](https://docs.djangoproject.com/en/5.2/ref/models/fields/)
6. **Open5e** — [https://open5e.com/](https://open5e.com/)
7. Cat Webling, **Breaking Down the Dungeons and Dragons Character Sheet — Part 1** (Medium) — [https://medium.com/super-jump/breaking-down-the-dungeons-and-dragons-character-sheet-part-1-18b4f02c4304](https://medium.com/super-jump/breaking-down-the-dungeons-and-dragons-character-sheet-part-1-18b4f02c4304)


