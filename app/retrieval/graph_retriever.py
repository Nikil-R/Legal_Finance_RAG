"""
Graph-Lite Retriever
Implements a conceptual knowledge graph using NetworkX.
Links legal and financial concepts to enhance context.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set

import networkx as nx

from app.utils.logger import get_logger

logger = get_logger(__name__)

class GraphRetriever:
    """
    Conceptual Knowledge Graph.
    Instead of full Neo4j, this uses NetworkX to store and traverse
    pre-defined and auto-extracted relationship between legal/finance concepts.
    """

    def __init__(self) -> None:
        self.graph = nx.Graph()
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self) -> None:
        """Seed the graph with foundational legal and finance links."""
        # Legal: Fundamental Rights
        self.graph.add_edge("Article 21", "Right to Life", relation="guarantees")
        self.graph.add_edge("Article 21", "Right to Privacy", relation="extended_interpretation")
        self.graph.add_edge("Right to Privacy", "Justice Puttaswamy v. Union of India", relation="landmark_judgment")
        self.graph.add_edge("Justice Puttaswamy v. Union of India", "Aadhaar Act", relation="challenges")
        
        # Legal: Basic Structure
        self.graph.add_edge("Basic Structure Doctrine", "Kesavananda Bharati case", relation="established_in")
        self.graph.add_edge("Basic Structure Doctrine", "Article 368", relation="limits_amendment_power")
        
        # Tax: Income Tax
        self.graph.add_edge("Section 80C", "Deductions", relation="category")
        self.graph.add_edge("Section 80C", "PPF", relation="eligible_investment")
        self.graph.add_edge("Section 80C", "ELSS", relation="eligible_investment")
        self.graph.add_edge("Section 87A", "Rebate", relation="benefit")
        self.graph.add_edge("Section 87A", "New Tax Regime", relation="enhanced_in")
        
        # Finance: GST
        self.graph.add_edge("GST", "Indirect Tax", relation="type")
        self.graph.add_edge("GST", "101st Amendment Act", relation="constitutional_basis")
        self.graph.add_edge("GST Council", "Article 279A", relation="constitutional_authority")

        logger.info("Conceptual Graph initialized with %d nodes and %d edges.", 
                    self.graph.number_of_nodes(), self.graph.number_of_edges())

    def get_related_concepts(self, concepts: List[str], depth: int = 1) -> Dict[str, List[Dict[str, str]]]:
        """
        Finds concepts related to the input set by traversing the graph.
        """
        results = {}
        processed_concepts = [c.lower() for c in concepts]
        
        # Match input keywords to graph nodes (case-insensitive fuzzy match)
        nodes_to_traverse = []
        for node in self.graph.nodes:
            low_node = str(node).lower()
            if any(pc in low_node or low_node in pc for pc in processed_concepts):
                nodes_to_traverse.append(node)

        for start_node in nodes_to_traverse:
            related = []
            # Find neighbors at specific depth
            neighbors = nx.single_source_shortest_path_length(self.graph, start_node, cutoff=depth)
            
            for nb, dist in neighbors.items():
                if dist == 0: continue
                # Get edge attributes for the direct relation if distance is 1
                if dist == 1:
                    edge_data = self.graph.get_edge_data(start_node, nb)
                    related.append({
                        "concept": str(nb),
                        "relation": edge_data.get("relation", "related"),
                        "distance": dist
                    })
                else:
                    related.append({
                        "concept": str(nb),
                        "relation": "indirectly_related",
                        "distance": dist
                    })
            
            if related:
                results[str(start_node)] = related

        return results

    def get_context_expansion(self, question: str) -> str:
        """
        Analyzes the question for known concepts and returns a string 
        of related knowledge to augment the RAG context.
        """
        # Simple keyword extraction (better if using NER or LLM)
        words = set(re.findall(r'\b\w+\b', question.lower()))
        
        # Look for multi-word concepts
        potential_concepts = []
        for node in self.graph.nodes:
            if str(node).lower() in question.lower():
                potential_concepts.append(str(node))
        
        if not potential_concepts:
            return ""

        related_map = self.get_related_concepts(potential_concepts)
        
        if not related_map:
            return ""

        expansion_blocks = ["### Supplemental Concept Knowledge (Graph RAG)"]
        for concept, relations in related_map.items():
            rel_str = ", ".join([f"{r['concept']} (via {r['relation']})" for r in relations[:3]])
            expansion_blocks.append(f"- {concept} is linked to: {rel_str}")
        
        return "\n".join(expansion_blocks)

import re
