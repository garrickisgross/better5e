from models.primitives import Skill, Stat
import dao.skill_dao as skill_dao, dao.stat_dao as stat_dao
import dao.init_db as init_db

def run():
    init_db.init_db()

    core_stats = [
        Stat(key="STR", name="Strength", default=True),
        Stat(key="DEX", name="Dexterity", default=True),
        Stat(key="CON", name="Constitution", default=True),
        Stat(key="INT", name="Intelligence", default=True),
        Stat(key="WIS", name="Wisdom", default=True),
        Stat(key="CHA", name="Charisma", default=True),
    ]

    for s in core_stats:
        if not stat_dao.get_by_key(s.key):
            stat_dao.insert(s)

    core_skills = [
        Skill(key="ACRBT", name="Acrobatics",      governing_stat_key="DEX", default=True),
        Skill(key="ANIMH", name="Animal Handling", governing_stat_key="WIS", default=True),
        Skill(key="ARCAN", name="Arcana",          governing_stat_key="INT", default=True),
        Skill(key="ATHLE", name="Athletics",       governing_stat_key="STR", default=True),
        Skill(key="DECEP", name="Deception",       governing_stat_key="CHA", default=True),
        Skill(key="HISTO", name="History",         governing_stat_key="INT", default=True),
        Skill(key="INSIG", name="Insight",         governing_stat_key="WIS", default=True),
        Skill(key="INTIM", name="Intimidation",    governing_stat_key="CHA", default=True),
        Skill(key="INVES", name="Investigation",   governing_stat_key="INT", default=True),
        Skill(key="MEDIC", name="Medicine",        governing_stat_key="WIS", default=True),
        Skill(key="NATUR", name="Nature",          governing_stat_key="INT", default=True),
        Skill(key="PERCE", name="Perception",      governing_stat_key="WIS", default=True),
        Skill(key="PERFO", name="Performance",     governing_stat_key="CHA", default=True),
        Skill(key="PERSU", name="Persuasion",      governing_stat_key="CHA", default=True),
        Skill(key="RELIG", name="Religion",        governing_stat_key="INT", default=True),
        Skill(key="SLEIG", name="Sleight of Hand", governing_stat_key="DEX", default=True),
        Skill(key="STEAL", name="Stealth",         governing_stat_key="DEX", default=True),
        Skill(key="SURVI", name="Survival",        governing_stat_key="WIS", default=True),
    ]

    for s in core_skills:
        if not skill_dao.get_by_key(s.key):
            skill_dao.insert(s)
    

if __name__ == "__main__":
    run() 