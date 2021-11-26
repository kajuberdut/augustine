import collections
import os
import re
import typing as t
from base64 import b32encode

from augustine_text.patterns import GREEDY_WHITESPACE, SENTENCE_END, TOKEN_END


def hash_word(word: str) -> int:
    p, m, pow, val = 31, 1e9 + 9, 1, 0

    def roll(char: str):
        nonlocal val, pow
        val = (val + (ord(char) - 96) * pow) % m
        pow = (pow * p) % m

    # Rolling forward and then in reverse reduces collisions
    [roll(char) for char in word]
    [roll(char) for char in word[::-1]]

    return int(val)


def ue_id() -> str:
    "Unique Enough Id"
    return b32encode(os.urandom(7)).decode("utf-8")[0:-4]


def sentencize(text: str) -> t.List[str]:
    text = re.sub(GREEDY_WHITESPACE, " ", text)
    return [s.strip() for s in re.split(SENTENCE_END, text) if s.strip()]


def tokenize(text: str) -> t.List[t.Dict[str, t.Any]]:
    return [w.strip() for w in re.split(TOKEN_END, text) if w.strip()]


if __name__ == "__main__":
    from collections import defaultdict
    import pathlib

    total_words = []

    path = pathlib.Path("/home/giblesnot/code/augustine-text")

    for p in path.iterdir():
        if p.is_file() and p.suffix == ".txt":
            with open(p, encoding="utf-8") as fh:
                text = fh.read()
            sentences = sentencize(text)
            [total_words.extend(tokenize(s)) for s in sentences]

    unique_words = list(set([w.lower() for w in total_words]))

    print(f"total words {len(total_words)}, unique words {len(unique_words)}")

    known = defaultdict(list)

    for w in unique_words:
        hash = hash_word(w)
        known[hash].append(w)

    collisions = [v for k, v in known.items() if len(v) > 1]
    print(f"{len(collisions)*1.00/len(unique_words)}% collisions")
    # print(collisions)
