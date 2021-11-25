import re


TOKEN_END = re.compile(r"([^\da-zA-Z'])")
SENTENCE_END = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s")
GREEDY_WHITESPACE = re.compile(r"\s+")
