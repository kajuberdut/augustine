from collections import defaultdict
from importlib import resources

from augustine_text import data
from augustine_text.utility import hash_word, sentencize, tokenize, ue_id
from ward import fixture, test
import typing as t
import bz2


MILLION = 1_000_000


@fixture
def word_list() -> t.List:
    with resources.as_file(resources.files(data)) as f:
        with open((f / "words.bz"), "rb") as bz_file:
            return bz2.decompress(bz_file.read()).decode("utf-8").split()


@test("Test for ue_id collisions")
def _():
    ids = [ue_id() for i in range(MILLION)]
    assert len(list(set(ids))) == len(ids)


@test("Test for word hashing collisions")
def _(word_list=word_list):

    known = defaultdict(list)

    [known[hash_word(w)].append(w) for w in word_list]
    collisions = [v for k, v in known.items() if len(v) > 1]

    collision_percent = (len(collisions) * 1.00 / len(word_list)) * 100
    assert collision_percent < 0.02
