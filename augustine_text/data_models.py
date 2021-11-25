import typing as t
from enum import Enum

from dsorm import Column, ForeignKey, Table, TypeHandler, UniqueConstraint, make_table

from augustine_text.utility import hash_word


class AdlerInt(int):
    pass


class AdlerHash(TypeHandler):
    sql_type = "AdlerHash"
    python_type = AdlerInt

    @staticmethod
    def to_sql(i: t.Union[str, int, bytes]) -> int:
        if isinstance(i, int):
            return i
        return hash_word(i)

    @staticmethod
    def to_python(i: int):
        return i


AdlerHash.register()


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
            python_type=AdlerInt,
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
    ],
    constraints=[
        words.fkey("a_word_id"),
        words.fkey("b_word_id"),
        ForeignKey(column="link_type_id", reference="LinkType.id"),
        UniqueConstraint(column=["a_word_id", "b_word_id", "link_type_id"]),
    ],
)

doc_links = Table(
    table_name="link",
    column=[
        Column(column_name="doc_id", python_type=int, nullable=False),
        Column(column_name="link_id", python_type=int, nullable=False),
        Column(column_name="incidence", python_type=int),
    ],
    constraints=[
        docs.fkey("doc_id"),
        links.fkey("link_id"),
        UniqueConstraint(column=["doc_id", "link_id"]),
    ],
)
