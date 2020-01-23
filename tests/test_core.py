
def test_get_nav():
    import pythainav as nav
    kt_nav = nav.get('KT-PRECIOUS')
    print(kt_nav)
    assert kt_nav.value >= 0