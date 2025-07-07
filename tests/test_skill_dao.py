import uuid
import pytest
from models.primitives import Skill, Stat
from dao import skill_dao, stat_dao
from dao.init_db import init_db

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    from dao import connection
    test_db = tmp_path / "test.sqlite3"
    monkeypatch.setattr(connection, "DB_PATH", test_db)
    init_db()


def test_insert_skills_without_stat_raises():
    dummy = Skill(
        id=uuid.uuid4(),
        key="STEAL",
        name="Stealth",
        governing_stat_key="CHA",
        default=False,
    )
    with pytest.raises(ValueError) as exc:
        skill_dao.insert(dummy)
    assert "Unknown Stat" in str(exc.value)


def test_insert_and_get_skill():
    # First insert a valid Stat
    stat = Stat(
        id=uuid.uuid4(),
        key="CHA",
        name="Charisma",
        description="",
        default=True,
    )
    stat_dao.insert(stat)

    skill = Skill(
        id=uuid.uuid4(),
        key="PERSU",
        name="Persuasion",
        governing_stat_key="CHA",
        default=False,
    )
    skill_dao.insert(skill)
    fetched = skill_dao.get_by_key("PERSU")
    assert isinstance(fetched, Skill)
    assert fetched.key == skill.key
    assert fetched.name == skill.name
    assert fetched.governing_stat_key == skill.governing_stat_key


def test_all_stats_for_skills():
    # Reuse 'charisma' stat
    stat = stat_dao.get_by_key("CHA")
    if stat is None:
        stat = Stat(
            id=uuid.uuid4(),
            key="CHA",
            name="Charisma",
            description="",
            default=True,
        )
        stat_dao.insert(stat)

    s1 = Skill(
        id=uuid.uuid4(),
        key="INTIM",
        name="Intimidation",
        governing_stat_key="CHA",
        default=False,
    )
    s2 = Skill(
        id=uuid.uuid4(),
        key="DECEP",
        name="Deception",
        governing_stat_key="CHA",
        default=True,
    )
    skill_dao.insert(s1)
    skill_dao.insert(s2)

    skills = skill_dao.all_stats()
    assert isinstance(skills, dict)
    assert set(skills.keys()) >= {"INTIM", "DECEP"}