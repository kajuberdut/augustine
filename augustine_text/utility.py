import collections
import os
import re
import typing as t
from base64 import b32encode
from zlib import adler32

from augustine_text.patterns import GREEDY_WHITESPACE, SENTENCE_END, TOKEN_END


def hash_word(word: t.Union[str, bytes]):
    if isinstance(word, str):
        word = word.encode()
    return adler32(word)


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

    with open("C:/Code/augustine/words_alpha.txt", "r") as f:
        lines = [w.strip() for w in f.readlines()]

    known = defaultdict(list)

    for w in lines:
        hash = hash_word(w+w[::-1])
        known[hash].append(w)

    collisions = [v for k,v in known.items() if len(v) > 1]
    print(f"{len(collisions)*1.00/len(lines)}% collisions")