from ward import test
from augustine_text.sample_text import words
from augustine_text.utility import ue_id

MILLION = 1_000_000


@test("Not a very good test")
def _():
    assert words(75)


@test("Test for id collisions")
def _():
    ids = [ue_id() for i in range(MILLION)]
    assert len(list(set(ids))) == len(ids)
