from better5e.modifiers import Modifier, ModifierOperation


def test_modifier_apply_operations():
    mod_add = Modifier(target="x", operation=ModifierOperation.ADD, value=2)
    assert mod_add.apply(3) == 5

    mod_mul = Modifier(target="x", operation=ModifierOperation.MULTIPLY, value=3)
    assert mod_mul.apply(4) == 12

    mod_set = Modifier(target="x", operation=ModifierOperation.SET, value=7)
    assert mod_set.apply(1) == 7

    mod_grant = Modifier(target="x", operation=ModifierOperation.GRANT, value=None)
    assert mod_grant.apply(5) == 5
