import dataclasses
import typing as t
from importlib import resources
from pathlib import Path
from sqlite3 import Connection

from dsorm import Database, Table, post_connect

from augustine_text import data
from augustine_text.data_models import LinkType, docs
from augustine_text.utility import hash_word, sentencize, tokenize, ue_id


@post_connect
def register_functions(db: Database, connection: Connection):
    db.functions_set = True
    connection.create_function("WordHash", 1, hash_word, deterministic=True)
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
                "id": hash_word(token.chars),
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

        db = get_db()
        db.execute(
            f""" 
        INSERT INTO word(id, word)
        SELECT DISTINCT newwords.id, newwords.word
        FROM [{temp_words.table_name}] newwords
        LEFT JOIN word oldwords ON newwords.id = oldwords.id
        WHERE oldwords.id IS NULL
        ;"""
        )

        db.execute(
            f"""
WITH temp_links AS (
 SELECT a_word.id a_word_id
	  , b_word.id b_word_id
	  , CASE
		    WHEN a_word.link_type_id = {LinkType.START.value} 
			    THEN {LinkType.START.value}
		    WHEN b_word.link_type_id = {LinkType.STOP.value} 
			    THEN {LinkType.STOP.value}
		    ELSE {LinkType.CONT.value}
	    END link_type_id
	, COUNT(*) incidence
	FROM [{temp_words.table_name}] a_word
	JOIN [{temp_words.table_name}] b_word ON a_word.sentence_id = a_word.sentence_id
						 AND a_word.i = (b_word.i -1)
	GROUP BY a_word.id
		   , b_word.id
		   , CASE
		    WHEN a_word.link_type_id = {LinkType.START.value} 
			    THEN {LinkType.START.value}
		    WHEN b_word.link_type_id = {LinkType.STOP.value} 
			    THEN {LinkType.STOP.value}
		    ELSE {LinkType.CONT.value}
	    END
)
INSERT INTO link (a_word_id, b_word_id, link_type_id, doc_id, incidence)
SELECT a_word_id
	, b_word_id
	, link_type_id
	, {self.id} doc_id
	, incidence
FROM temp_links
WHERE true
ON CONFLICT(a_word_id, b_word_id, link_type_id, doc_id)
DO UPDATE SET
incidence = (link.incidence + excluded.incidence)
WHERE link.doc_id = excluded.doc_id
AND link.a_word_id = excluded.a_word_id
AND link.b_word_id = excluded.b_word_id
AND link.link_type_id = excluded.link_type_id
        ;"""
        )
        temp_words.drop().execute()


if __name__ == "__main__":
    from importlib import resources

    db = get_db().initialize()

    d = Doc.from_string("test", "This is a word list. This is another sentence.").save()
