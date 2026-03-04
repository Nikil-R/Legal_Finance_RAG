"""
Correctness scoring - measures if the answer matches the expected answer.
"""

import re
from dataclasses import dataclass


@dataclass
class CorrectnessResult:
    """Result of correctness evaluation."""

    score: float  # 0.0 to 1.0
    keyword_matches: int
    keywords_expected: int
    matched_keywords: list[str]
    missing_keywords: list[str]
    explanation: str


class CorrectnessScorer:
    """
    Evaluates if the generated answer is correct based on expected answer.

    Uses keyword matching approach since exact string matching is too strict
    and LLM-based evaluation would be too expensive/slow for CI.
    """

    def __init__(self):
        pass

    def score(
        self, answer: str, expected_answer: str, required_keywords: list[str]
    ) -> CorrectnessResult:
        """
        Score the correctness of an answer.

        Args:
            answer: The generated answer
            expected_answer: The expected/reference answer
            required_keywords: List of keywords that must appear

        Returns:
            CorrectnessResult with score and details
        """
        if not answer:
            return CorrectnessResult(
                score=0.0,
                keyword_matches=0,
                keywords_expected=len(required_keywords),
                matched_keywords=[],
                missing_keywords=required_keywords,
                explanation="Empty answer",
            )

        answer_lower = answer.lower()

        # Check required keywords
        matched = []
        missing = []

        for keyword in required_keywords:
            keyword_lower = keyword.lower()

            # Check for exact match or close variations
            if self._keyword_present(keyword_lower, answer_lower):
                matched.append(keyword)
            else:
                missing.append(keyword)

        # Calculate score
        if required_keywords:
            keyword_score = len(matched) / len(required_keywords)
        else:
            # No required keywords - fall back to semantic similarity
            keyword_score = self._simple_similarity(
                answer.lower(), expected_answer.lower()
            )

        return CorrectnessResult(
            score=keyword_score,
            keyword_matches=len(matched),
            keywords_expected=len(required_keywords),
            matched_keywords=matched,
            missing_keywords=missing,
            explanation=f"Matched {len(matched)}/{len(required_keywords)} required keywords",
        )

    def _keyword_present(self, keyword: str, text: str) -> bool:
        """Check if a keyword is present in text, with variations."""
        # Direct match
        if keyword in text:
            return True

        # Handle numbers with formatting variations
        # e.g., "1,50,000" should match "150000" or "1.5 lakh"
        if re.search(r"\d", keyword):
            # Remove formatting and check
            keyword_digits = re.sub(r"[^\d]", "", keyword)
            text_digits = re.sub(r"[^\d]", "", text)
            if keyword_digits and keyword_digits in text_digits:
                return True

        # Handle section references
        # e.g., "Section 80C" should match "80C" or "section 80c"
        section_match = re.search(r"section\s*(\d+\w*)", keyword, re.IGNORECASE)
        if section_match:
            section_num = section_match.group(1).lower()
            if section_num in text:
                return True

        return False

    def _simple_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple word overlap similarity."""
        words1 = set(re.findall(r"\b\w{3,}\b", text1))
        words2 = set(re.findall(r"\b\w{3,}\b", text2))

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)
