import os
import re
import typing as t
from base64 import b32encode

from augustine_text.patterns import GREEDY_WHITESPACE, SENTENCE_END, TOKEN_END


def hash_word(word: str) -> int:
    pow, val = 1, 0
    
    def roll(char: str):
        nonlocal val, pow
        val = (val + (ord(char) - 96) * pow) % 1_000_000_009.0
        pow = (pow * 31) % 1_000_000_009.0

    # Rolling forward and then in reverse reduces collisions
    [roll(char) for char in (word + word[::-1])]

    return int(val)


def ue_id() -> str:
    "Unique Enough Id"
    return b32encode(os.urandom(7)).decode("utf-8")[0:-4]


def sentencize(text: str) -> t.List[str]:
    text = re.sub(GREEDY_WHITESPACE, " ", text)
    return [s.strip() for s in re.split(SENTENCE_END, text) if s.strip()]


def tokenize(text: str) -> t.List[t.Dict[str, t.Any]]:
    return [w.strip() for w in re.split(TOKEN_END, text) if w.strip()]

# cd .\augustine_text\
# python -m nuitka --module .\utility.py
