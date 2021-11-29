import os
import re
import typing as t
from base64 import b32encode

from augustine_text.patterns import GREEDY_WHITESPACE, SENTENCE_END, TOKEN_END
import hashlib


def hash_word(text: str):
    return int.from_bytes(
        hashlib.sha256(text.encode("utf-8")).digest()[:8], byteorder="big", signed=True
    )


def ue_id() -> str:
    "Unique Enough Id"
    return b32encode(os.urandom(7)).decode("utf-8")[0:-4]


def sentencize(text: str) -> t.List[str]:
    text = re.sub(GREEDY_WHITESPACE, " ", text)
    return [s.strip() for s in re.split(SENTENCE_END, text) if s.strip()]


def tokenize(text: str) -> t.List[t.Dict[str, t.Any]]:
    return [w.strip() for w in re.split(TOKEN_END, text) if w.strip()]
