import dataclasses
import typing as t
from importlib import resources
from pathlib import Path
from sqlite3 import Connection

from dsorm import Column, Database, Table, post_connect

from augustine_text import data
from augustine_text.data_models import LinkType, docs
from augustine_text.utility import hash_word, sentencize, tokenize, ue_id


@post_connect
def register_functions(db: Database, connection: Connection):
    db.functions_set = True
    connection.create_function("AdlerHash", 1, hash_word, deterministic=True)
    db.remove_hooks(hook_name="post_connect_hook")

def get_db_path() -> Path:
    with resources.as_file(resources.files(data)) as f:
        return f / "august_data.db"


def get_db():
    return Database(db_path=get_db_path(), is_default=True)


@dataclasses.dataclass
class Token:
    """A Token is a set of one or more characters."""

    chars: str


@dataclasses.dataclass
class Sentence:
    "A sentence is a sequence of tokens with a fixed order."

    tokens: t.List[Token]
    _id: str = dataclasses.field(default_factory=ue_id)

    @classmethod
    def from_string(cls, text: str) -> "Sentence":
        return cls(tokens=[Token(t) for t in tokenize(text=text)])

    @property
    def id(self) -> str:
        return self._id

    @property
    def token_list(self) -> t.List[Token]:
        return self.tokens

    @property
    def type_list(self) -> t.List[LinkType]:
        return (
            [LinkType.START]
            + [LinkType.CONT for i in range(len(self.tokens) - 2)]
            + [LinkType.STOP]
        )

    @property
    def order_list(self) -> t.List[int]:
        return [i for i, v in enumerate(self.tokens)]

    @property
    def token_data(self):
        return [
            {
                "word": token.chars,
                "i": order,
                "link_type_id": link_type,
                "sentence_id": self.id,
            }
            for order, token, link_type in zip(
                self.order_list, self.token_list, self.type_list
            )
        ]


@dataclasses.dataclass
class Doc:
    "A document is a sequence of sentences with a fixed order."
    doc_name: str
    _sentences: t.List[Sentence]
    _id: int = dataclasses.field(default=None)

    @classmethod
    def from_string(cls, doc_name: str, text: str) -> "Doc":
        return cls(
            doc_name=doc_name,
            _sentences=[Sentence.from_string(s) for s in sentencize(text)],
        )

    @property
    def sentences(self):
        return self._sentences

    @property
    def id(self):
        if self._id is None:
            results = docs.select(where={"doc_name": self.doc_name}).execute()
            if not results:
                docs.insert(data={"doc_name": self.doc_name}).execute()
                results = docs.select(where={"doc_name": self.doc_name}).execute()

            self._id = results[0]["id"]
        return self._id

    @property
    def data(self):
        result = []
        [result.extend(s.token_data) for s in self.sentences]
        return result

    def save(self):
        temp_words = Table.from_data(
            table_name=f"temp_words_{ue_id()}",
            data=self.data,
            temp=True,
        )
        temp_words.execute()

        temp_links = Table(
            table_name=f"temp_links_{ue_id()}",
            column=[
                Column(column_name="a_word_id", python_type=int),
                Column(column_name="b_word_id", python_type=int),
                Column(column_name="link_type_id", python_type=int),
                Column(column_name="incidence", python_type=int),
            ],
            temp=True,
        )
        temp_links.execute()

        db = get_db()
        db.execute(
            f""" 
        INSERT INTO word(id, word)
        SELECT DISTINCT AdlerHash(newwords.word), newwords.word
        FROM [{temp_words.table_name}] newwords
        LEFT JOIN word oldwords ON newwords.word = oldwords.word
        WHERE oldwords.word IS NULL
        ;"""
        )

        # db.execute(
        #     f"""
        # WITH new_links AS (
        #     SELECT word.id word_id
        #         , new.i
        #         , new.link_type_id
        #         , new.sentence_id
        #     FROM [{temp_words.table_name}] new
        #     JOIN word ON new.word = word.word
        # )
        # INSERT INTO [{temp_links.table_name}] (a_word_id, b_word_id, link_type_id, incidence)
        # SELECT a_word.word_id
        #     , b_word.word_id
        #     , CASE
        #         WHEN a_word.link_type_id = {LinkType.START.value} THEN {LinkType.START.value}
        #         WHEN b_word.link_type_id = {LinkType.STOP.value} THEN {LinkType.STOP.value}
        #         ELSE {LinkType.CONT.value}
        #     END link_type_id
        #     , COUNT(*) incidence
        # FROM new_links a_word
        # JOIN new_links b_word ON a_word.sentence_id = a_word.sentence_id
        #                      AND a_word.i = (b_word.i -1)
        # GROUP BY a_word.word_id
        #        , b_word.word_id
        #        , CASE
        #             WHEN a_word.link_type_id = {LinkType.START.value} THEN {LinkType.START.value}
        #             WHEN b_word.link_type_id = {LinkType.STOP.value} THEN {LinkType.STOP.value}
        #             ELSE {LinkType.CONT.value}
        #          END
        # ;"""
        # )

        # db.execute(
        #     f"""
        # INSERT INTO link (doc_id, a_word_id, b_word_id, link_type_id, incidence)
        # SELECT {self.id} doc_id
        #     , a_word_id
        #     , b_word_id
        #     , link_type_id
        #     , incidence
        # FROM [{temp_links.table_name}]
        # WHERE true
        # ON CONFLICT(doc_id, a_word_id, b_word_id, link_type_id)
        # DO UPDATE SET
        # incidence = (link.incidence + excluded.incidence)
        # WHERE link.doc_id = excluded.doc_id
        # AND link.a_word_id = excluded.a_word_id
        # AND link.b_word_id = excluded.b_word_id
        # AND link.link_type_id = excluded.link_type_id
        # ;"""
        # )
        temp_words.drop().execute()
        # temp_links.drop().execute()


if __name__ == "__main__":
    # db = get_db().initialize()

    # txt = """Sentence one.
    # Sentence Two. Sentence Three four five.
    # """

    # d = Doc.from_string("some name", txt).save()
