"""A tiny document store with keyword search over IT-support guides.

Each guide is a Markdown file: the first line is ``# Title``, the rest is the text.
The file name (without ``.md``) is the document id that answers cite as their source.

Search is plain keyword overlap: a document's score is the fraction of the
query's words that appear in it (ties go to the document that mentions them
more often). It's simple enough to read in a minute and completely deterministic. Real systems use embeddings; the agent logic is the same.
"""
from __future__ import annotations

import re
from pathlib import Path

from common.mocks.base import MockService

DEFAULT_DOCS_DIR = Path(__file__).parent / "data" / "docs"

STOPWORDS = {
    "the", "and", "for", "you", "your", "can", "cant", "not", "how", "what", "with", "this", "that",
    "are", "but", "have", "has", "was", "from", "my", "our", "its", "into", "will", "when", "why",
    "does", "doesnt", "dont", "any", "all", "get", "got", "use", "using", "need", "please", "help",
    "cannot", "after", "again", "keep", "keeps", "say", "says", "just", "still", "some", "there",
    "should", "would", "could", "shall",
}


class DocumentNotFound(KeyError):
    """No document with that id."""


def _tokens(text: str) -> list[str]:
    """Lower-case content words, roughly stemmed, in order (repeats kept)."""
    tokens = []
    for word in re.findall(r"[a-z0-9]+", text.lower().replace("'", "").replace("-", "")):  # "Wi-Fi" -> "wifi"
        if len(word) < 3 or word in STOPWORDS:
            continue
        for suffix in ("ing", "ed", "es", "s"):  # crude stemming: "connecting" -> "connect"
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                word = word[: -len(suffix)]
                break
        tokens.append(word)
    return tokens


def _words(text: str) -> set[str]:
    return set(_tokens(text))


class DocumentStore(MockService):
    def __init__(
        self,
        docs_dir: Path | str | None = None,
        extra_docs_dirs: list[Path | str] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._docs: dict[str, dict] = {}
        for folder in [docs_dir or DEFAULT_DOCS_DIR, *(extra_docs_dirs or [])]:
            for path in sorted(Path(folder).glob("*.md")):
                lines = path.read_text(encoding="utf-8").strip().splitlines()
                title = lines[0].lstrip("# ").strip() if lines else path.stem
                text = "\n".join(lines[1:]).strip()
                self._docs[path.stem] = {"doc_id": path.stem, "title": title, "text": text}

    def list_ids(self) -> list[str]:
        return sorted(self._docs)

    def search(self, query: str, k: int = 3, min_score: float = 0.0) -> list[dict]:
        """The ``k`` best-matching documents for ``query``, best first.

        Each hit has ``doc_id``, ``title``, ``score`` (0–1) and the best-matching
        paragraph as ``snippet``. Documents with no matching words are left out.
        """
        self._begin("search", {"query": query, "k": k})
        query_words = _words(query)
        if not query_words:
            return []
        ranked = []
        for doc in self._docs.values():
            doc_tokens = _tokens(doc["title"] + " " + doc["text"])
            found = query_words & set(doc_tokens)
            score = round(len(found) / len(query_words), 2)
            if score > 0 and score >= min_score:
                mentions = sum(1 for t in doc_tokens if t in query_words)  # tie-breaker
                hit = {"doc_id": doc["doc_id"], "title": doc["title"], "score": score,
                       "snippet": self._best_paragraph(doc["text"], query_words)}
                ranked.append((-score, -mentions, doc["doc_id"], hit))
        ranked.sort(key=lambda r: r[:3])
        return [r[3] for r in ranked[:k]]

    def get(self, doc_id: str) -> dict:
        """The full document. Raises ``DocumentNotFound`` for an unknown id."""
        self._begin("get", {"doc_id": doc_id})
        if doc_id not in self._docs:
            raise DocumentNotFound(f"No document with id {doc_id!r}. Known ids: {', '.join(self.list_ids())}")
        return dict(self._docs[doc_id])

    @staticmethod
    def _best_paragraph(text: str, query_words: set[str], limit: int = 400) -> str:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        best = max(paragraphs, key=lambda p: len(query_words & _words(p)), default="")
        return best if len(best) <= limit else best[: limit - 1] + "…"
