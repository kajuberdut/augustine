import typing as t
from importlib import resources
from pathlib import Path
from random import choice

# def sample_text(source_name="Lorem Ipsum") -> "Markov":
#     with get_included_path(source_name.lower().split()[0]) as f:
#         m = Markov.from_mseedfile(f)
#     return m

# def words(c: int):
#     generators = [sample_text(t) for t in INCLUDED]
#     result = []
#     while c > 0:
#         sentence = choice(generators).sentence()
#         if (l := len(sentence)) > c:
#             sentence = sentence[:c]
#         result.append(sentence)
#         c -= l
#     return "\n".join(
#             [" ".join(s).capitalize() for s in result]
#         )


# if __name__ == "__main__":
#     print(words(15))
