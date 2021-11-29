import typing as t
from enum import Enum

from dsorm import Column, ForeignKey, Table, TypeHandler, UniqueConstraint, make_table

from augustine_text.utility import hash_word


class WordHashInt(int):
    pass

    @classmethod
    def from_string(cls, word: t.Union[str, bytes]) -> "WordHashInt":
        if isinstance(word, bytes):
            word = word.decode(encoding="utf-8")
        return cls(hash_word(word))


class WordHash(TypeHandler):
    sql_type = "WordHashInt"
    python_type = WordHashInt

    @staticmethod
    def to_sql(i: t.Union[str, int, bytes]) -> int:
        if isinstance(i, int):
            return i
        return WordHashInt.from_string(i)

    @staticmethod
    def to_python(i: int):
        return i


WordHash.register()


@make_table
class LinkType(Enum):
    START = 1
    STOP = 2
    CONT = 3


words = Table(
    table_name="word",
    column=[
        Column(
            column_name="id",
            python_type=WordHashInt,
            pkey=True,
        ),
        Column(column_name="word", python_type=str, nullable=False, unique=True),
    ],
)


docs = Table(
    table_name="doc",
    column=[Column.id(), Column(column_name="doc_name", python_type=str, unique=True)],
)


links = Table(
    table_name="link",
    column=[
        Column.id(),
        Column(column_name="a_word_id", python_type=int, nullable=False),
        Column(column_name="b_word_id", python_type=int, nullable=False),
        Column(column_name="link_type_id", python_type=LinkType, nullable=False),
        Column(column_name="doc_id", python_type=int, nullable=False),
        Column(column_name="incidence", python_type=int),
    ],
    constraints=[
        words.fkey("a_word_id"),
        words.fkey("b_word_id"),
        ForeignKey(column="link_type_id", reference="LinkType.id"),
        docs.fkey("doc_id"),
        UniqueConstraint(column=["a_word_id", "b_word_id", "doc_id", "link_type_id"]),
    ],
)
