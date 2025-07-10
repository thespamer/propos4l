from typing import Dict, List, Optional, Union
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.embeddings import OpenAIEmbeddings
import numpy as np

from app.models.database import BlockType
from app.services.vector_store import VectorStore, IndexType
from app.services.pattern_analyzer import PatternAnalyzer

class SuggestionEngine:
    def __init__(self, vector_store: VectorStore, pattern_analyzer: PatternAnalyzer):
        self.vector_store = vector_store
        self.pattern_analyzer = pattern_analyzer
        self.llm = OpenAI(temperature=0.5)
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize suggestion prompts
        self.content_suggestion_prompt = PromptTemplate(
            input_variables=[
                "block_type",
                "current_content",
                "similar_blocks",
                "patterns",
                "client_info"
            ],
            template="""Analyze this {block_type} section and suggest improvements:

Current Content:
{current_content}

Similar High-Quality Examples:
{similar_blocks}

Common Patterns and Best Practices:
{patterns}

Client Information:
{client_info}

Provide 3-5 specific suggestions to improve this content. Focus on:
1. Content structure and completeness
2. Language and tone
3. Formatting and presentation
4. Industry-specific improvements

Format each suggestion as:
- Description: [brief description]
- Reasoning: [why this would improve the proposal]
- Example: [short example of the improvement]"""
        )
        
        self.section_suggestion_prompt = PromptTemplate(
            input_variables=[
                "missing_sections",
                "client_info",
                "industry_patterns"
            ],
            template="""Based on analysis of similar proposals, suggest additional sections that could strengthen this proposal:

Missing Sections:
{missing_sections}

Client Information:
{client_info}

Industry Patterns:
{industry_patterns}

For each suggested section, explain:
1. Why it would be valuable
2. What content it should include
3. Where it should be placed in the proposal"""
        )
        
        # Initialize LLM chains
        self.content_chain = LLMChain(llm=self.llm, prompt=self.content_suggestion_prompt)
        self.section_chain = LLMChain(llm=self.llm, prompt=self.section_suggestion_prompt)
    
    async def get_content_suggestions(
        self,
        block_type: BlockType,
        content: str,
        client_info: Dict,
        confidence_threshold: float = 0.7
    ) -> Dict:
        """
        Get suggestions for improving specific content based on patterns and similar blocks
        """
        # Get similar high-quality blocks
        similar_blocks = await self.vector_store.search_similar_blocks(
            content=content,
            block_type=block_type,
            k=5,
            confidence_threshold=confidence_threshold
        )
        
        # Get pattern analysis
        patterns = await self.pattern_analyzer.analyze_block_patterns(block_type)
        
        # Format similar blocks text
        similar_blocks_text = "\n---\n".join([
            f"Example (similarity: {block['similarity_score']:.2f}):\n{block['content']}"
            for block in similar_blocks
        ])
        
        # Format patterns text
        patterns_text = []
        if patterns:
            # Language patterns
            if 'language_patterns' in patterns:
                patterns_text.append("Language Patterns:")
                for key, stats in patterns['language_patterns'].items():
                    if 'mean' in stats:
                        patterns_text.append(
                            f"- {key}: typically {stats['mean']:.1f} (range: {stats['min']}-{stats['max']})"
                        )
            
            # Formatting patterns
            if 'formatting_patterns' in patterns:
                patterns_text.append("\nFormatting Patterns:")
                fmt = patterns['formatting_patterns']
                if 'feature_usage' in fmt:
                    for feature, pct in fmt['feature_usage'].items():
                        if pct > 50:
                            patterns_text.append(f"- {feature}: used in {pct:.0f}% of cases")
        
        # Get suggestions from LLM
        suggestions = await self.content_chain.arun(
            block_type=block_type.value,
            current_content=content,
            similar_blocks=similar_blocks_text,
            patterns="\n".join(patterns_text),
            client_info=str(client_info)
        )
        
        return {
            'suggestions': suggestions,
            'similar_blocks': similar_blocks,
            'patterns': patterns
        }
    
    async def get_section_suggestions(
        self,
        current_sections: List[BlockType],
        client_info: Dict
    ) -> Dict:
        """
        Suggest additional sections that could improve the proposal
        """
        # Get all block types
        all_block_types = set(BlockType)
        missing_sections = all_block_types - set(current_sections)
        
        if not missing_sections:
            return {'suggestions': [], 'missing_sections': []}
        
        # Get industry-specific patterns
        industry = client_info.get('industry', '')
        industry_blocks = await self.vector_store.search(
            query=industry,
            k=50,
            index_type=IndexType.DOCUMENT,
            filters={'industry': industry}
        )
        
        # Analyze section frequency in industry
        section_counts = {block_type: 0 for block_type in missing_sections}
        total_docs = len(industry_blocks)
        
        for doc in industry_blocks:
            sections = doc.get('sections', {})
            for section in sections:
                try:
                    block_type = BlockType(section)
                    if block_type in missing_sections:
                        section_counts[block_type] += 1
                except ValueError:
                    continue
        
        # Calculate section frequencies
        section_frequencies = {
            block_type: (count / total_docs) * 100
            for block_type, count in section_counts.items()
        }
        
        # Format missing sections info
        missing_sections_text = []
        for block_type in missing_sections:
            freq = section_frequencies.get(block_type, 0)
            if freq > 0:
                missing_sections_text.append(
                    f"{block_type.value}: present in {freq:.1f}% of {industry} proposals"
                )
        
        # Get suggestions from LLM
        suggestions = await self.section_chain.arun(
            missing_sections="\n".join(missing_sections_text),
            client_info=str(client_info),
            industry_patterns=f"Analysis based on {total_docs} proposals in the {industry} industry."
        )
        
        return {
            'suggestions': suggestions,
            'missing_sections': [s.value for s in missing_sections],
            'section_frequencies': section_frequencies
        }
    
    async def get_smart_suggestions(
        self,
        proposal_content: Dict,
        client_info: Dict
    ) -> Dict:
        """
        Get comprehensive suggestions for improving the entire proposal
        """
        suggestions = {
            'content_suggestions': {},
            'section_suggestions': None,
            'overall_quality': {}
        }
        
        # Get content suggestions for each section
        current_sections = []
        for section, content in proposal_content.items():
            try:
                block_type = BlockType(section)
                current_sections.append(block_type)
                
                if content.strip():  # Only analyze non-empty sections
                    section_suggestions = await self.get_content_suggestions(
                        block_type=block_type,
                        content=content,
                        client_info=client_info
                    )
                    suggestions['content_suggestions'][section] = section_suggestions
            except ValueError:
                continue
        
        # Get suggestions for missing sections
        section_suggestions = await self.get_section_suggestions(
            current_sections=current_sections,
            client_info=client_info
        )
        suggestions['section_suggestions'] = section_suggestions
        
        # Calculate overall quality metrics
        quality_metrics = {
            'completeness': len(current_sections) / len(BlockType) * 100,
            'sections_with_suggestions': len(suggestions['content_suggestions']),
            'missing_critical_sections': [
                section for section in section_suggestions['missing_sections']
                if section_suggestions['section_frequencies'].get(section, 0) > 70
            ]
        }
        suggestions['overall_quality'] = quality_metrics
        
        return suggestions
