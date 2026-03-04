"""
Faithfulness scoring - measures if the answer is grounded in the retrieved context.
"""
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class FaithfulnessResult:
    """Result of faithfulness evaluation."""
    score: float  # 0.0 to 1.0
    is_grounded: bool
    claims_found: int
    claims_supported: int
    unsupported_claims: list[str]
    explanation: str


class FaithfulnessScorer:
    """
    Evaluates if the generated answer is faithful to the source documents.
    
    A faithful answer:
    1. Only contains information present in the sources
    2. Does not hallucinate facts
    3. Properly attributes claims to sources
    """
    
    def __init__(self):
        pass
    
    def score(
        self,
        answer: str,
        context: str,
        sources: list[dict]
    ) -> FaithfulnessResult:
        """
        Score the faithfulness of an answer to its source context.
        
        Args:
            answer: The generated answer
            context: The context string that was provided to the LLM
            sources: List of source documents used
        
        Returns:
            FaithfulnessResult with score and details
        """
        if not answer or not context:
            return FaithfulnessResult(
                score=0.0,
                is_grounded=False,
                claims_found=0,
                claims_supported=0,
                unsupported_claims=[],
                explanation="Empty answer or context"
            )
        
        # Extract claims from the answer (simple sentence-based approach)
        claims = self._extract_claims(answer)
        
        if not claims:
            return FaithfulnessResult(
                score=1.0,
                is_grounded=True,
                claims_found=0,
                claims_supported=0,
                unsupported_claims=[],
                explanation="No factual claims found in answer"
            )
        
        # Check each claim against the context
        supported_claims = 0
        unsupported = []
        
        context_lower = context.lower()
        
        for claim in claims:
            if self._is_claim_supported(claim, context_lower):
                supported_claims += 1
            else:
                unsupported.append(claim)
        
        # Calculate score
        score = supported_claims / len(claims) if claims else 1.0
        
        return FaithfulnessResult(
            score=score,
            is_grounded=score >= 0.7,
            claims_found=len(claims),
            claims_supported=supported_claims,
            unsupported_claims=unsupported[:5],  # Limit to top 5
            explanation=f"{supported_claims}/{len(claims)} claims supported by context"
        )
    
    def _extract_claims(self, answer: str) -> list[str]:
        """
        Extract factual claims from the answer.
        Simple approach: split into sentences and filter.
        """
        # Remove disclaimer section
        answer = re.split(r'---\s*\n?\s*\*?\*?Disclaimer', answer, flags=re.IGNORECASE)[0]
        
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', answer)
        
        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Skip very short sentences
            if len(sentence) < 20:
                continue
            
            # Skip questions
            if sentence.endswith('?'):
                continue
            
            # Skip purely structural sentences
            if sentence.lower().startswith(('the following', 'here are', 'below are')):
                continue
            
            claims.append(sentence)
        
        return claims
    
    def _is_claim_supported(self, claim: str, context_lower: str) -> bool:
        """
        Check if a claim is supported by the context.
        
        Uses keyword overlap approach - a claim is supported if
        significant keywords from the claim appear in the context.
        """
        # Extract significant words from the claim
        claim_words = self._extract_keywords(claim.lower())
        
        if not claim_words:
            return True  # No significant words to check
        
        # Count how many keywords appear in context
        matches = sum(1 for word in claim_words if word in context_lower)
        
        # Require at least 50% keyword overlap
        overlap_ratio = matches / len(claim_words) if claim_words else 1.0
        
        return overlap_ratio >= 0.5
    
    def _extract_keywords(self, text: str) -> list[str]:
        """Extract significant keywords from text."""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
            'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'under', 'again', 'further', 'then', 'once', 'and',
            'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither', 'not',
            'only', 'own', 'same', 'than', 'too', 'very', 'just', 'also', 'this',
            'that', 'these', 'those', 'such', 'which', 'who', 'whom', 'whose',
            'what', 'where', 'when', 'why', 'how', 'all', 'each', 'every', 'any',
            'some', 'no', 'other', 'most', 'more', 'less', 'few', 'many', 'much'
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', text)
        
        # Filter stop words and return unique keywords
        keywords = [w for w in words if w not in stop_words]
        
        return list(set(keywords))
