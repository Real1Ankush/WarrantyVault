from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


texts = [
    "Boat BassHeads 900 Wired Headphone with Mic",
    "Sony MDR-EX15AP EX Stereo Headphones with Mic",
    "Yonex Astrox 68 D Badminton Racket",
]

queries = [
    "my headphones stopped working",
    "my cans are broken",
    "badminton racket",
]


for query in queries:

    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    )

    text_embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    similarities = model.similarity(
        model.encode(
            [query],
            normalize_embeddings=True,
        ),
        model.encode(
            texts,
            normalize_embeddings=True,
        ),
    )[0]

    print("\n==============================")
    print("QUERY:", query)
    print("==============================")

    for text, score in zip(
        texts,
        similarities.tolist(),
    ):
        print(
            f"{score:.4f}  |  {text}"
        )