from typing import Dict, List, Optional, Union
from pathlib import Path
import jinja2
from weasyprint import HTML
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import os
import json

from app.models.database import BlockType
from app.services.vector_store import VectorStore, IndexType
from app.services.pattern_analyzer import PatternAnalyzer

class ProposalGenerator:
    def __init__(self, vector_store: VectorStore):
        self.template_dir = Path("templates")
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=jinja2.select_autoescape(['html'])
        )
        
        # Initialize services
        self.vector_store = vector_store
        self.pattern_analyzer = PatternAnalyzer(vector_store)
        
        # Initialize LangChain components
        self.llm = OpenAI(temperature=0.7)
        self.embeddings = OpenAIEmbeddings()
        
        # Define proposal section prompts with pattern guidance
        self.section_prompt = PromptTemplate(
            input_variables=[
                "section_type",
                "client_info",
                "similar_sections",
                "patterns",
                "requirements"
            ],
            template="""Generate a {section_type} section for a business proposal with these requirements:
            
            Client Information:
            {client_info}
            
            Similar sections from other proposals:
            {similar_sections}
            
            Common patterns and recommendations:
            {patterns}
            
            Specific Requirements:
            {requirements}
            
            Generate a well-structured {section_type} section that follows the common patterns and addresses the requirements.
            Make sure to use appropriate formatting (bullet points, paragraphs) based on the patterns.
            The tone should be professional and persuasive."""
        )
        
        # Initialize LLM chain
        self.section_chain = LLMChain(llm=self.llm, prompt=self.section_prompt)

    async def generate_proposal(self, params: Dict) -> Dict:
        """
        Generate a new proposal based on input parameters, using pattern analysis and similar proposals
        """
        try:
            proposal_content = {}
            
            # Generate each section using patterns and similar content
            for block_type in BlockType:
                section_content = await self._generate_section(
                    block_type=block_type,
                    params=params
                )
                proposal_content[block_type.value] = section_content
            
            # Add metadata
            proposal_content['metadata'] = {
                'client_name': params.get('client_name', 'Cliente'),
                'industry': params.get('industry', 'Technology'),
                'date_generated': params.get('date', ''),
                'version': '1.0'
            }
            
            return proposal_content
            
        except Exception as e:
            raise Exception(f"Error generating proposal: {str(e)}")
    
    async def _generate_section(self, block_type: BlockType, params: Dict) -> str:
        """
        Generate a specific section using pattern analysis and similar blocks
        """
        # Get similar blocks from vector store
        similar_blocks = await self.vector_store.search(
            query=params.get('requirements', ''),
            k=5,
            index_type=block_type,
            filters={'industry': params.get('industry')}
        )
        
        # Get pattern analysis for this block type
        patterns = await self.pattern_analyzer.analyze_block_patterns(block_type)
        
        # Format similar sections text
        similar_sections = []
        for block in similar_blocks:
            score = block.get('similarity_score', 0)
            if score >= 0.7:
                similar_sections.append(
                    f"Example (similarity: {score:.2f}):\n{block['content']}"
                )
        similar_sections_text = "\n---\n".join(similar_sections)
        
        # Format pattern recommendations
        pattern_recommendations = []
        if patterns:
            lang_patterns = patterns.get('language_patterns', {})
            fmt_patterns = patterns.get('formatting_patterns', {})
            
            if lang_patterns:
                pattern_recommendations.append("Language Patterns:")
                for key, stats in lang_patterns.items():
                    if 'mean' in stats:
                        pattern_recommendations.append(
                            f"- {key}: typically {stats['mean']:.1f} (range: {stats['min']}-{stats['max']})"
                        )
            
            if fmt_patterns:
                pattern_recommendations.append("\nFormatting Patterns:")
                if 'common_fonts' in fmt_patterns:
                    pattern_recommendations.append("- Common fonts: " + ", ".join(fmt_patterns['common_fonts'].keys()))
                if 'feature_usage' in fmt_patterns:
                    features = fmt_patterns['feature_usage']
                    for feature, pct in features.items():
                        if pct > 50:
                            pattern_recommendations.append(f"- {feature}: used in {pct:.0f}% of cases")
        
        # Generate section content
        result = await self.section_chain.arun(
            section_type=block_type.value,
            client_info=json.dumps({
                'name': params.get('client_name', 'Cliente'),
                'industry': params.get('industry', 'Technology'),
                'requirements': params.get('requirements', ''),
                'scope': params.get('scope', ''),
                'timeline': params.get('timeline', ''),
                'budget': params.get('budget', '')
            }, indent=2),
            similar_sections=similar_sections_text,
            patterns="\n".join(pattern_recommendations),
            requirements=params.get('requirements', '')
        )
        
        return result

    def export_to_pdf(self, content: Dict, template_name: str = "proposal.html") -> bytes:
        """
        Export proposal content to PDF using WeasyPrint
        """
        template = self.env.get_template(template_name)
        html_content = template.render(**content)
        pdf = HTML(string=html_content).write_pdf()
        return pdf

    def export_to_markdown(self, content: Dict) -> str:
        """
        Export proposal content to Markdown format
        """
        markdown = f"""# {content['title']}

## Contexto
{content['context']}

## Solução Proposta
{content['solution']}

## Escopo
{content['scope']}

## Cronograma
{content['timeline']}

## Investimento
{content['investment']}
"""
        return markdown
