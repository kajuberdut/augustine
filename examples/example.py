from augustine_text.sample_text import words


# 75K words of procedurally generated text
# This is about the length of novel.
text = words(75000)
text_length = len(text)


print(text[:100])
