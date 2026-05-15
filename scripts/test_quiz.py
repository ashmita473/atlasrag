import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from core.ingestion.loader import DocumentLoader
from core.ingestion.preprocessor import TextPreprocessor
from core.ingestion.chunker import TextChunker

from core.pipelines.quiz_chain import QuizChain


loader = DocumentLoader()

preprocessor = TextPreprocessor()

chunker = TextChunker()

quiz_chain = QuizChain()


document = loader.load_file(
    "sample.pdf"
)

clean_docs = preprocessor.process_documents(
    document.pages
)

chunks = chunker.split(
    clean_docs
)

quiz = quiz_chain.generate(
    chunks,
    n=3,
    difficulty="easy"
)

print("\n=== GENERATED QUIZ ===\n")

for i, q in enumerate(quiz):

    print(f"\nQuestion {i + 1}")

    print(q["question"])

    for idx, option in enumerate(q["options"]):

        print(f"{chr(65 + idx)}. {option}")

    print(f"\nAnswer: {q['answer']}")

    print(f"Explanation: {q['explanation']}")