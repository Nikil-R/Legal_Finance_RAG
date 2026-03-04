"""
Citation quality scoring - measures if citations are present and valid.
"""
from dataclasses import dataclass
import re


@dataclass
class CitationQualityResult:
    """Result of citation quality evaluation."""
    score: float  # 0.0 to 1.0
    has_citations: bool
    citations_found: list[int]
    citations_expected: int
    invalid_citations: list[int]
    has_disclaimer: bool
    explanation: str


class CitationQualityScorer:
    """
    Evaluates the quality of citations in the answer.
    
    Checks:
    1. Are citations present?
    2. Are citation numbers valid (reference existing sources)?
    3. Are citations appropriately distributed?
    4. Is the disclaimer present?
    """
    
    def __init__(self):
        self.citation_pattern = re.compile(r'\[(\d+)\]')
        self.disclaimer_patterns = [
            r'disclaimer',
            r'educational purposes',
            r'not.{0,20}(legal|financial|professional).{0,20}advice',
            r'consult.{0,30}professional'
        ]
    
    def score(
        self,
        answer: str,
        num_sources: int,
        expected_citations: int = 1
    ) -> CitationQualityResult:
        """
        Score the citation quality of an answer.
        
        Args:
            answer: The generated answer
            num_sources: Number of source documents available
            expected_citations: Minimum expected citation count
        
        Returns:
            CitationQualityResult with score and details
        """
        if not answer:
            return CitationQualityResult(
                score=0.0,
                has_citations=False,
                citations_found=[],
                citations_expected=expected_citations,
                invalid_citations=[],
                has_disclaimer=False,
                explanation="Empty answer"
            )
        
        # Find all citations
        citations = [int(m) for m in self.citation_pattern.findall(answer)]
        unique_citations = list(set(citations))
        
        # Check for invalid citations
        invalid = [c for c in unique_citations if c < 1 or c > num_sources]
        valid = [c for c in unique_citations if c not in invalid]
        
        # Check for disclaimer
        has_disclaimer = self._check_disclaimer(answer)
        
        # Calculate score
        score = self._calculate_score(
            has_citations=len(valid) > 0,
            valid_count=len(valid),
            invalid_count=len(invalid),
            expected=expected_citations,
            has_disclaimer=has_disclaimer
        )
        
        return CitationQualityResult(
            score=score,
            has_citations=len(valid) > 0,
            citations_found=unique_citations,
            citations_expected=expected_citations,
            invalid_citations=invalid,
            has_disclaimer=has_disclaimer,
            explanation=self._generate_explanation(valid, invalid, has_disclaimer)
        )
    
    def _check_disclaimer(self, answer: str) -> bool:
        """Check if the answer contains a disclaimer."""
        answer_lower = answer.lower()
        
        for pattern in self.disclaimer_patterns:
            if re.search(pattern, answer_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_score(
        self,
        has_citations: bool,
        valid_count: int,
        invalid_count: int,
        expected: int,
        has_disclaimer: bool
    ) -> float:
        """Calculate the overall citation quality score."""
        score = 0.0
        
        # Citation presence (40%)
        if has_citations:
            score += 0.4
        
        # Citation validity (30%)
        if valid_count > 0:
            validity_ratio = valid_count / (valid_count + invalid_count)
            score += 0.3 * validity_ratio
        
        # Disclaimer presence (30%)
        if has_disclaimer:
            score += 0.3
        
        return score
    
    def _generate_explanation(
        self,
        valid: list[int],
        invalid: list[int],
        has_disclaimer: bool
    ) -> str:
        """Generate explanation string."""
        parts = []
        
        if valid:
            parts.append(f"Found valid citations: {valid}")
        else:
            parts.append("No valid citations found")
        
        if invalid:
            parts.append(f"Invalid citations: {invalid}")
        
        if has_disclaimer:
            parts.append("Disclaimer present")
        else:
            parts.append("Disclaimer missing")
        
        return "; ".join(parts)
