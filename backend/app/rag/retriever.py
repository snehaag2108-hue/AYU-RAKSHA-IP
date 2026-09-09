import json
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.config import settings


class LocalRAG:
    """
    Lightweight source-grounded RAG engine.

    Loads JSON knowledge records from the configured
    knowledge directory and retrieves the most relevant
    evidence using TF-IDF similarity.
    """

    def __init__(self):
        self.docs: List[Dict[str, Any]] = []
        self.vectorizer = None
        self.matrix = None
        self.load()

    def load(self):

        self.docs = []

        root = Path(
            settings.knowledge_dir
        )

        root.mkdir(
            parents=True,
            exist_ok=True
        )

        for path in sorted(
            root.glob("*.json")
        ):

            try:

                data = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

                if isinstance(
                    data,
                    list
                ):

                    for item in data:

                        if not isinstance(
                            item,
                            dict
                        ):
                            continue

                        if not item.get(
                            "text"
                        ):
                            continue

                        self.docs.append(
                            item
                        )

            except Exception as exc:

                print(
                    f"Knowledge load warning: {path.name}: {exc}"
                )


        if not self.docs:

            self.vectorizer = None
            self.matrix = None

            print(
                "RAG: no knowledge documents found."
            )

            return


        texts = [
            self._build_search_text(
                doc
            )
            for doc in self.docs
        ]


        self.vectorizer = (
            TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                sublinear_tf=True
            )
        )


        self.matrix = (
            self.vectorizer.fit_transform(
                texts
            )
        )


        print(
            f"RAG loaded {len(self.docs)} source records."
        )


    def _build_search_text(
        self,
        doc: Dict[str, Any]
    ) -> str:

        parts = [

            str(
                doc.get(
                    "title",
                    ""
                )
            ),

            str(
                doc.get(
                    "type",
                    ""
                )
            ),

            str(
                doc.get(
                    "authority",
                    ""
                )
            ),

            str(
                doc.get(
                    "jurisdiction",
                    ""
                )
            ),

            str(
                doc.get(
                    "text",
                    ""
                )
            )

        ]

        return " ".join(parts)


    def reload(self):

        """
        Reload knowledge files without
        restarting the whole application.
        """

        self.load()


    def search(
        self,
        query: str,
        top_k: int = 5
    ):

        if (
            not query
            or not query.strip()
        ):
            return []


        if (
            not self.docs
            or self.vectorizer is None
            or self.matrix is None
        ):
            return []


        query_vector = (
            self.vectorizer.transform(
                [query]
            )
        )


        scores = (
            self.matrix @
            query_vector.T
        ).toarray().ravel()


        indices = np.argsort(
            scores
        )[::-1]


        results = []


        for index in indices:

            score = float(
                scores[index]
            )


            if score <= 0:
                continue


            document = dict(
                self.docs[index]
            )


            document[
                "relevance_score"
            ] = round(
                score,
                4
            )


            results.append(
                document
            )


            if len(results) >= top_k:
                break


        return results


    def search_with_threshold(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.05
    ):

        results = self.search(
            query,
            top_k
        )


        return [
            item
            for item in results
            if item.get(
                "relevance_score",
                0
            ) >= threshold
        ]


    def context(
        self,
        query: str,
        top_k: int = 5
    ):

        results = self.search(
            query,
            top_k
        )


        context = []


        for item in results:

            context.append({

                "title":
                    item.get(
                        "title"
                    ),

                "authority":
                    item.get(
                        "authority"
                    ),

                "jurisdiction":
                    item.get(
                        "jurisdiction"
                    ),

                "version":
                    item.get(
                        "version"
                    ),

                "source_url":
                    item.get(
                        "source_url"
                    ),

                "text":
                    item.get(
                        "text"
                    ),

                "relevance_score":
                    item.get(
                        "relevance_score",
                        0
                    )

            })


        return context


# Global RAG instance
rag = LocalRAG()