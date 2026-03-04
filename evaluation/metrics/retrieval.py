"""
Retrieval relevance scoring - measures if retrieved chunks are relevant.
"""

from dataclasses import dataclass


@dataclass
class RetrievalRelevanceResult:
    """Result of retrieval relevance evaluation."""

    score: float  # 0.0 to 1.0
    chunks_retrieved: int
    relevant_chunks: int
    top_score: float
    avg_score: float
    domain_match: bool
    explanation: str


class RetrievalRelevanceScorer:
    """
    Evaluates the relevance of retrieved chunks.

    Checks:
    1. Were chunks retrieved?
    2. Do chunks have high relevance scores?
    3. Do chunks match the expected domain?
    4. Do chunks contain expected keywords?
    """

    def __init__(self, relevance_threshold: float = 0.3):
        """
        Initialize scorer.

        Args:
            relevance_threshold: Minimum score to consider a chunk relevant
        """
        self.relevance_threshold = relevance_threshold

    def score(
        self, sources: list[dict], expected_domain: str, required_keywords: list[str]
    ) -> RetrievalRelevanceResult:
        """
        Score the relevance of retrieved sources.

        Args:
            sources: List of retrieved source documents
            expected_domain: The domain of the question
            required_keywords: Keywords that should appear in sources

        Returns:
            RetrievalRelevanceResult with score and details
        """
        if not sources:
            return RetrievalRelevanceResult(
                score=0.0,
                chunks_retrieved=0,
                relevant_chunks=0,
                top_score=0.0,
                avg_score=0.0,
                domain_match=False,
                explanation="No chunks retrieved",
            )

        # Extract relevance scores
        scores = []
        for src in sources:
            # Handle different score field names
            score = src.get("relevance_score") or src.get("rerank_score") or 0.0
            scores.append(score)

        top_score = max(scores) if scores else 0.0
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Count relevant chunks (above threshold)
        relevant_count = sum(1 for s in scores if s >= self.relevance_threshold)

        # Check domain match
        domain_match = False
        if expected_domain == "all":
            domain_match = True
        else:
            for src in sources:
                if src.get("domain") == expected_domain:
                    domain_match = True
                    break

        # Check keyword presence in sources
        keyword_score = self._check_keywords_in_sources(sources, required_keywords)

        # Calculate overall score
        overall_score = self._calculate_score(
            retrieved=len(sources),
            relevant=relevant_count,
            top_score=top_score,
            domain_match=domain_match,
            keyword_score=keyword_score,
        )

        return RetrievalRelevanceResult(
            score=overall_score,
            chunks_retrieved=len(sources),
            relevant_chunks=relevant_count,
            top_score=top_score,
            avg_score=avg_score,
            domain_match=domain_match,
            explanation=f"Retrieved {len(sources)} chunks, {relevant_count} above threshold",
        )

    def _check_keywords_in_sources(
        self, sources: list[dict], keywords: list[str]
    ) -> float:
        """Check what fraction of keywords appear in sources."""
        if not keywords:
            return 1.0

        # Combine all source content
        all_content = " ".join(
            str(src.get("content", "") or src.get("excerpt", "")) for src in sources
        ).lower()

        # Check each keyword
        found = sum(1 for kw in keywords if kw.lower() in all_content)

        return found / len(keywords) if keywords else 1.0

    def _calculate_score(
        self,
        retrieved: int,
        relevant: int,
        top_score: float,
        domain_match: bool,
        keyword_score: float,
    ) -> float:
        """Calculate overall retrieval relevance score."""
        if retrieved == 0:
            return 0.0

        # Component scores
        retrieval_ratio = min(relevant / retrieved, 1.0) if retrieved > 0 else 0.0
        domain_score = 1.0 if domain_match else 0.5

        # Weighted average
        score = (
            0.3 * retrieval_ratio
            + 0.3 * min(top_score, 1.0)
            + 0.2 * domain_score
            + 0.2 * keyword_score
        )

        return score
