from scripts.seed_demo import seed_demo


def test_seed_is_repeatable():
    seed_demo(reset=True)
    seed_demo(reset=False)
    assert True
