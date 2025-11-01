

docs = {
    "doc1": "the cat sat",
    "doc2": "the dog sat",
    "doc3": "the cat ate"
}

unique_words = set(word for text in docs.values() for word in text.lower().split())
print(unique_words)


inverted_index = {}
for word in unique_words:
    inverted_index[word] = set()
    for item in docs:
        if word in docs[item].lower().split():
            inverted_index[word].add(item)

print(inverted_index)







